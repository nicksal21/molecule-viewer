"""
Main molecular editor class
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import math

from components import *
from element_data import *
from periodic_table_dialog import PeriodicTableDialog

class MolecularEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("2D/3D Molecular Editor")
        self.root.geometry("1400x800")
        
        # Data structures
        self.atoms = {}
        self.bonds = []
        self.next_atom_id = 0
        self.selected_atoms = set()
        
        # Current tools and settings
        self.current_tool = ToolType.NONE
        self.current_element = 'C'
        self.current_bond_type = BondType.SINGLE
        self.bg_color_3d = '#808080'
        
        # Tool buttons tracking
        self.tool_buttons = {}
        
        # Drag state
        self.drag_start = None
        self.drag_atom = None
        
        # Bond creation state
        self.bond_start_atom = None
        
        # Selection state
        self.selection_start = None
        self.selection_rect = None
        self.lasso_points = []
        self.lasso_line = None
        
        # Canvas settings
        self.atom_radius = ATOM_RADIUS_2D
        self.bond_length = BOND_LENGTH_2D
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - 2D Editor and tools
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.setup_tool_panel(left_frame)
        self.setup_canvas(left_frame)
        
        # Right side - 3D Viewer
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_3d_viewer(right_frame)
        
        # Status bars
        self.status_bar = ttk.Label(self.root, text="Ready - No tool selected", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.element_info = ttk.Label(self.root, text="", relief=tk.SUNKEN)
        self.element_info.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_tool_panel(self, parent):
        tool_frame = ttk.LabelFrame(parent, text="Tools")
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Basic tools
        basic_frame = ttk.LabelFrame(tool_frame, text="Basic Tools")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tools = [
            ('drag', "Drag", ToolType.DRAG),
            ('delete', "Delete", ToolType.DELETE),
            ('select_rect', "Select (Rect)", ToolType.SELECT_RECT),
            ('select_lasso', "Select (Lasso)", ToolType.SELECT_LASSO)
        ]
        
        for key, text, tool_type in tools:
            self.tool_buttons[key] = tk.Button(
                basic_frame, text=text, relief=tk.RAISED,
                command=lambda t=tool_type: self.toggle_tool(t)
            )
            self.tool_buttons[key].pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Separator(basic_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)
        
        # Add cleanup button
        ttk.Button(basic_frame, text="Clean Up Structure", 
                command=self.cleanup_structure).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(basic_frame, text="Clear All", command=self.clear_all).pack(fill=tk.X, padx=5, pady=2)
        
        # Element tools
        element_frame = ttk.LabelFrame(tool_frame, text="Elements")
        element_frame.pack(fill=tk.X, padx=5, pady=5)
        
        element_grid = ttk.Frame(element_frame)
        element_grid.pack(fill=tk.X, padx=5, pady=2)
        
        for i, element in enumerate(COMMON_ELEMENTS):
            btn_key = f'element_{element}'
            color = get_element_color(element)
            text_color = 'white' if should_use_white_text(element) else 'black'
            self.tool_buttons[btn_key] = tk.Button(
                element_grid, text=element, width=4, relief=tk.RAISED,
                command=lambda e=element: self.select_element_tool(e),
                bg=color, fg=text_color
            )
            self.tool_buttons[btn_key].grid(row=i//2, column=i%2, padx=2, pady=2)
        
        ttk.Button(element_frame, text="Periodic Table", command=self.show_periodic_table).pack(fill=tk.X, padx=5, pady=2)
        
        # Bond tools
        bond_frame = ttk.LabelFrame(tool_frame, text="Bonds")
        bond_frame.pack(fill=tk.X, padx=5, pady=5)
        
        bond_types = [
            (BondType.SINGLE, "Single (—)"),
            (BondType.DOUBLE, "Double (=)"),
            (BondType.TRIPLE, "Triple (≡)"),
            (BondType.WEDGE, "Wedge (▲)"),
            (BondType.HASH, "Hash (|||)")
        ]
        
        for bond_type, label in bond_types:
            btn_key = f'bond_{bond_type.name}'
            self.tool_buttons[btn_key] = tk.Button(
                bond_frame, text=label, relief=tk.RAISED,
                command=lambda bt=bond_type: self.select_bond_tool(bt)
            )
            self.tool_buttons[btn_key].pack(fill=tk.X, padx=5, pady=2)
        
        # Charge tools
        charge_frame = ttk.LabelFrame(tool_frame, text="Charge")
        charge_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tool_buttons['charge_pos'] = tk.Button(
            charge_frame, text="e+", relief=tk.RAISED,
            command=lambda: self.toggle_tool(ToolType.CHARGE_POSITIVE)
        )
        self.tool_buttons['charge_pos'].pack(side=tk.LEFT, padx=5, pady=2)
        
        self.tool_buttons['charge_neg'] = tk.Button(
            charge_frame, text="e-", relief=tk.RAISED,
            command=lambda: self.toggle_tool(ToolType.CHARGE_NEGATIVE)
        )
        self.tool_buttons['charge_neg'].pack(side=tk.LEFT, padx=5, pady=2)

    def setup_canvas(self, parent):
        canvas_frame = ttk.LabelFrame(parent, text="2D Editor")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas_2d = tk.Canvas(canvas_frame, bg='white', width=600, height=600)
        self.canvas_2d.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize zoom and pan variables
        self.canvas_zoom = 1.0
        self.canvas_pan_x = 0
        self.canvas_pan_y = 0
        self.pan_start = None
        
        # Bind canvas events
        self.canvas_2d.bind("<Button-1>", self.on_canvas_click)
        self.canvas_2d.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas_2d.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas_2d.bind("<Button-3>", self.on_right_click)
        
        # Bind zoom and pan events
        self.canvas_2d.bind("<MouseWheel>", self.on_canvas_mousewheel)  # Windows
        self.canvas_2d.bind("<Button-4>", self.on_canvas_mousewheel)  # Linux scroll up
        self.canvas_2d.bind("<Button-5>", self.on_canvas_mousewheel)  # Linux scroll down
        self.canvas_2d.bind("<Button-2>", self.on_middle_mouse_down)  # Middle mouse for pan
        self.canvas_2d.bind("<B2-Motion>", self.on_middle_mouse_drag)
        self.canvas_2d.bind("<ButtonRelease-2>", self.on_middle_mouse_release)
    
    def setup_3d_viewer(self, parent):
        # 3D controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Reload 3D", command=self.update_3d_view).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Background:").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Black", command=lambda: self.set_3d_bg('#000000')).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="White", command=lambda: self.set_3d_bg('#FFFFFF')).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Gray", command=lambda: self.set_3d_bg('#808080')).pack(side=tk.LEFT, padx=2)
        
        # 3D Viewer
        viewer_frame = ttk.LabelFrame(parent, text="3D Viewer")
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.fig_3d = plt.Figure(figsize=(6, 6), dpi=100)
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.setup_3d_view()
        
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, viewer_frame)
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_3d_view(self):
        self.ax_3d.set_facecolor(self.bg_color_3d)
        self.ax_3d.set_axis_off()
        self.ax_3d.grid(False)
        self.ax_3d.set_xticks([])
        self.ax_3d.set_yticks([])
        self.ax_3d.set_zticks([])
    
    # Tool management methods
    def toggle_tool(self, tool_type, element=None, bond_type=None):
        if self.current_tool == tool_type:
            if tool_type == ToolType.ELEMENT and self.current_element == element:
                self.deactivate_all_tools()
                return
            elif tool_type == ToolType.BOND and self.current_bond_type == bond_type:
                self.deactivate_all_tools()
                return
            elif tool_type not in [ToolType.ELEMENT, ToolType.BOND]:
                self.deactivate_all_tools()
                return
        
        self.deactivate_all_tools()
        self.current_tool = tool_type
        
        # Update button appearance
        button_map = {
            ToolType.DRAG: 'drag',
            ToolType.DELETE: 'delete',
            ToolType.SELECT_RECT: 'select_rect',
            ToolType.SELECT_LASSO: 'select_lasso',
            ToolType.CHARGE_POSITIVE: 'charge_pos',
            ToolType.CHARGE_NEGATIVE: 'charge_neg'
        }
        
        if tool_type in button_map:
            self.tool_buttons[button_map[tool_type]].config(relief=tk.SUNKEN, bg='lightblue')
        elif tool_type == ToolType.ELEMENT:
            btn_key = f'element_{element}'
            if btn_key in self.tool_buttons:
                self.tool_buttons[btn_key].config(relief=tk.SUNKEN)
            self.current_element = element
            self.update_element_info(element)
        elif tool_type == ToolType.BOND:
            btn_key = f'bond_{bond_type.name}'
            if btn_key in self.tool_buttons:
                self.tool_buttons[btn_key].config(relief=tk.SUNKEN, bg='lightblue')
            self.current_bond_type = bond_type
        
        self.update_status_message()
        
    def cleanup_structure(self):
        """Clean up the molecular structure"""
        from molecular_cleanup import cleanup_structure
        cleanup_structure(self)
        self.update_status_message()
    
    def deactivate_all_tools(self):
        self.current_tool = ToolType.NONE
        self.bond_start_atom = None
        
        for key, btn in self.tool_buttons.items():
            if key.startswith('element_'):
                element = key.replace('element_', '')
                color = get_element_color(element)
                text_color = 'white' if should_use_white_text(element) else 'black'
                btn.config(relief=tk.RAISED, bg=color, fg=text_color)
            else:
                btn.config(relief=tk.RAISED, bg='SystemButtonFace')
        
        self.element_info.config(text="")
        self.update_status_message()
    
    def select_element_tool(self, element):
        self.toggle_tool(ToolType.ELEMENT, element=element)
    
    def select_bond_tool(self, bond_type):
        self.toggle_tool(ToolType.BOND, bond_type=bond_type)
        self.bond_start_atom = None
    
    def update_element_info(self, element_symbol):
        info = get_element_info(element_symbol)
        text = f"{info['name']} ({element_symbol}) - Atomic #: {info['number']}, Mass: {info['mass']:.2f}"
        self.element_info.config(text=text)
    
    def update_status_message(self):
        messages = {
            ToolType.NONE: "No tool selected",
            ToolType.DRAG: "Tool: Drag - Click and drag atoms to move them",
            ToolType.DELETE: "Tool: Delete - Click on atoms or bonds to delete",
            ToolType.SELECT_RECT: "Tool: Rectangle Selection - Drag to select atoms",
            ToolType.SELECT_LASSO: "Tool: Lasso Selection - Draw around atoms to select",
            ToolType.CHARGE_POSITIVE: "Tool: Add positive charge - Click on atoms",
            ToolType.CHARGE_NEGATIVE: "Tool: Add negative charge - Click on atoms"
        }
        
        if self.current_tool == ToolType.ELEMENT:
            msg = f"Tool: Add {self.current_element} atom - Click to place"
        elif self.current_tool == ToolType.BOND:
            if self.bond_start_atom:
                msg = f"Tool: {self.current_bond_type.name} bond - Click second atom"
            else:
                msg = f"Tool: {self.current_bond_type.name} bond - Click first atom"
        else:
            msg = messages.get(self.current_tool, "Ready")
        
        self.status_bar.config(text=msg)
    
    def show_periodic_table(self):
        PeriodicTableDialog(self.root, self.select_element_tool)
    
    # Canvas event handlers
    def on_canvas_click(self, event):
        from canvas_handlers import handle_canvas_click
        handle_canvas_click(self, event)
    
    def on_canvas_drag(self, event):
        from canvas_handlers import handle_canvas_drag
        handle_canvas_drag(self, event)
    
    def on_canvas_release(self, event):
        from canvas_handlers import handle_canvas_release
        handle_canvas_release(self, event)
    
    def on_right_click(self, event):
        from canvas_handlers import handle_right_click
        handle_right_click(self, event)
    
    # Other methods (simplified references)
    def get_atom_at(self, x, y):
        from canvas_operations import get_atom_at
        return get_atom_at(self, x, y)
    
    def create_atom(self, x, y):
        from canvas_operations import create_atom
        return create_atom(self, x, y)
    
    def create_bond(self, atom1_id, atom2_id):
        from canvas_operations import create_bond
        return create_bond(self, atom1_id, atom2_id)
    
    def delete_atom(self, atom_id):
        from canvas_operations import delete_atom
        delete_atom(self, atom_id)
    
    def move_atom(self, atom_id, dx, dy):
        from canvas_operations import move_atom
        move_atom(self, atom_id, dx, dy)
    
    def clear_all(self):
        response = messagebox.askyesno("Clear All", "Are you sure you want to clear all atoms and bonds?")
        if response:
            self.canvas_2d.delete("all")
            self.atoms.clear()
            self.bonds.clear()
            self.selected_atoms.clear()
            self.next_atom_id = 0
            self.bond_start_atom = None
    
    def set_3d_bg(self, color):
        self.bg_color_3d = color
        self.ax_3d.set_facecolor(color)
        self.canvas_3d.draw()
    
    def update_3d_view(self):
        from viewer_3d import update_3d_view
        update_3d_view(self)
        
    def on_canvas_mousewheel(self, event):
        """Handle mouse wheel for zoom"""
        # Get mouse position for zoom center
        x = self.canvas_2d.canvasx(event.x)
        y = self.canvas_2d.canvasy(event.y)
        
        # Determine zoom factor
        if event.delta:
            # Windows
            scale = 1.1 if event.delta > 0 else 0.9
        else:
            # Linux
            scale = 1.1 if event.num == 4 else 0.9
        
        # Update zoom
        self.canvas_zoom *= scale
        
        # Apply zoom to all canvas items
        self.canvas_2d.scale("all", x, y, scale, scale)
        
        # Update stored positions for atoms
        for atom in self.atoms.values():
            atom.x = x + (atom.x - x) * scale
            atom.y = y + (atom.y - y) * scale
            atom.radius *= scale

    def on_middle_mouse_down(self, event):
        """Start panning with middle mouse button"""
        self.canvas_2d.scan_mark(event.x, event.y)
        self.pan_start = (event.x, event.y)

    def on_middle_mouse_drag(self, event):
        """Pan the canvas"""
        self.canvas_2d.scan_dragto(event.x, event.y, gain=1)
        
        # Update pan offset
        if self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas_pan_x += dx
            self.canvas_pan_y += dy
            self.pan_start = (event.x, event.y)
            
            # Update atom positions
            for atom in self.atoms.values():
                atom.x += dx
                atom.y += dy

    def on_middle_mouse_release(self, event):
        """Stop panning"""
        self.pan_start = None

    def reset_canvas_view(self):
        """Reset canvas zoom and pan"""
        # Reset zoom
        if self.canvas_zoom != 1.0:
            scale = 1.0 / self.canvas_zoom
            self.canvas_2d.scale("all", 0, 0, scale, scale)
            
            # Update atom positions and radii
            for atom in self.atoms.values():
                atom.x *= scale
                atom.y *= scale
                atom.radius = get_element_radius_2d(atom.element)
        
        # Reset pan
        self.canvas_2d.xview_moveto(0)
        self.canvas_2d.yview_moveto(0)
        
        self.canvas_zoom = 1.0
        self.canvas_pan_x = 0
        self.canvas_pan_y = 0
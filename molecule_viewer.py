import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
import periodictable as pt
import colorsys

def get_element_color(element_symbol):
    """Get color for element with specific colors for common elements and dynamic generation for groups"""
    
    # Explicitly defined colors for common elements
    explicit_colors = {
        'H': '#FFFFFF',   # White
        'C': '#000000',   # Black
        'N': '#0000FF',   # Bright blue
        'O': '#FF0000',   # Bright red
        'F': '#00FF00',   # Bright green
        'S': '#FFFF00',   # Yellow
        'P': '#FFA500',   # Orange
        'Cl': '#00FF7F',  # Spring green
        'Br': '#8B4513',  # Brown
        'I': '#8B008B',   # Purple
    }
    
    if element_symbol in explicit_colors:
        return explicit_colors[element_symbol]
    
    try:
        element = getattr(pt, element_symbol)
        num = element.number
        
        # Determine group and position for dynamic color generation
        if element_symbol in ['Li', 'Na', 'K', 'Rb', 'Cs', 'Fr']:
            # Alkali metals - Red gradient
            base_hue = 0  # Red
            position = ['Li', 'Na', 'K', 'Rb', 'Cs', 'Fr'].index(element_symbol)
            saturation = 0.8
            lightness = 0.7 - (position * 0.1)  # Gets darker
            
        elif element_symbol in ['Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra']:
            # Alkaline earth - Orange gradient
            base_hue = 30  # Orange
            position = ['Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra'].index(element_symbol)
            saturation = 0.7
            lightness = 0.75 - (position * 0.1)
            
        elif element_symbol in ['He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn', 'Og']:
            # Noble gases - Cyan gradient
            base_hue = 180  # Cyan
            position = ['He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn', 'Og'].index(element_symbol)
            saturation = 0.5
            lightness = 0.8 - (position * 0.1)
            
        elif 57 <= num <= 71:  # Lanthanides
            base_hue = 200  # Blue
            position = num - 57
            saturation = 0.6
            lightness = 0.75 - (position * 0.03)
            
        elif 89 <= num <= 103:  # Actinides
            base_hue = 120  # Green
            position = num - 89
            saturation = 0.6
            lightness = 0.75 - (position * 0.03)
            
        elif element_symbol in ['B', 'Al', 'Ga', 'In', 'Tl', 'Nh']:
            # Boron group - Pink gradient
            base_hue = 320  # Pink
            position = ['B', 'Al', 'Ga', 'In', 'Tl', 'Nh'].index(element_symbol)
            saturation = 0.6
            lightness = 0.75 - (position * 0.1)
            
        elif element_symbol in ['Si', 'Ge', 'Sn', 'Pb', 'Fl']:
            # Carbon group - Green-brown gradient
            base_hue = 60  # Yellow-green
            position = ['Si', 'Ge', 'Sn', 'Pb', 'Fl'].index(element_symbol)
            saturation = 0.5
            lightness = 0.7 - (position * 0.12)
            
        elif element_symbol in ['As', 'Sb', 'Bi', 'Mc']:
            # Pnictogens - Purple gradient
            base_hue = 270  # Purple
            position = ['As', 'Sb', 'Bi', 'Mc'].index(element_symbol)
            saturation = 0.6
            lightness = 0.7 - (position * 0.12)
            
        elif element_symbol in ['Se', 'Te', 'Po', 'Lv']:
            # Chalcogens - Red-orange gradient
            base_hue = 15  # Red-orange
            position = ['Se', 'Te', 'Po', 'Lv'].index(element_symbol)
            saturation = 0.7
            lightness = 0.7 - (position * 0.12)
            
        elif element_symbol in ['At', 'Ts']:
            # Halogens continuation
            base_hue = 150  # Blue-green
            position = ['At', 'Ts'].index(element_symbol)
            saturation = 0.6
            lightness = 0.5 - (position * 0.15)
            
        else:
            # Transition metals - by group
            transition_groups = {
                # Group 3-4
                'Sc': (40, 0), 'Y': (40, 1), 'La': (40, 2), 'Ac': (40, 3),
                'Ti': (45, 0), 'Zr': (45, 1), 'Hf': (45, 2), 'Rf': (45, 3),
                # Group 5-6
                'V': (50, 0), 'Nb': (50, 1), 'Ta': (50, 2), 'Db': (50, 3),
                'Cr': (55, 0), 'Mo': (55, 1), 'W': (55, 2), 'Sg': (55, 3),
                # Group 7-8
                'Mn': (280, 0), 'Tc': (280, 1), 'Re': (280, 2), 'Bh': (280, 3),
                'Fe': (25, 0), 'Ru': (25, 1), 'Os': (25, 2), 'Hs': (25, 3),
                # Group 9-10
                'Co': (220, 0), 'Rh': (220, 1), 'Ir': (220, 2), 'Mt': (220, 3),
                'Ni': (160, 0), 'Pd': (160, 1), 'Pt': (160, 2), 'Ds': (160, 3),
                # Group 11-12
                'Cu': (30, 0), 'Ag': (30, 1), 'Au': (30, 2), 'Rg': (30, 3),
                'Zn': (210, 0), 'Cd': (210, 1), 'Hg': (210, 2), 'Cn': (210, 3),
            }
            
            if element_symbol in transition_groups:
                base_hue, position = transition_groups[element_symbol]
                saturation = 0.6
                lightness = 0.75 - (position * 0.15)
            else:
                # Default gray for unknown
                return '#808080'
        
        # Convert HSL to RGB
        rgb = colorsys.hls_to_rgb(base_hue/360, lightness, saturation)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        )
        return hex_color
        
    except:
        return '#808080'  # Default gray

class ToolType(Enum):
    NONE = 0
    DRAG = 1
    DELETE = 2
    SELECT_RECT = 3
    SELECT_LASSO = 4
    ELEMENT = 5
    BOND = 6
    CHARGE_POSITIVE = 7
    CHARGE_NEGATIVE = 8

class BondType(Enum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    WEDGE = 4
    HASH = 5

@dataclass
class Atom:
    element: str
    x: float
    y: float
    z: float = 0.0
    charge: int = 0
    id: int = None
    canvas_id: int = None
    text_id: int = None
    radius: float = 25  # Canvas radius for click detection

@dataclass
class Bond:
    atom1_id: int
    atom2_id: int
    bond_type: BondType
    canvas_id: int = None

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
        self.atom_radius = 25
        self.bond_length = 80
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - 2D Editor and tools
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tool panel
        tool_frame = ttk.LabelFrame(left_frame, text="Tools")
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Basic tools
        basic_frame = ttk.LabelFrame(tool_frame, text="Basic Tools")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tool_buttons['drag'] = tk.Button(basic_frame, text="Drag", relief=tk.RAISED,
                                              command=lambda: self.toggle_tool(ToolType.DRAG))
        self.tool_buttons['drag'].pack(fill=tk.X, padx=5, pady=2)
        
        self.tool_buttons['delete'] = tk.Button(basic_frame, text="Delete", relief=tk.RAISED,
                                                command=lambda: self.toggle_tool(ToolType.DELETE))
        self.tool_buttons['delete'].pack(fill=tk.X, padx=5, pady=2)
        
        self.tool_buttons['select_rect'] = tk.Button(basic_frame, text="Select (Rect)", relief=tk.RAISED,
                                                     command=lambda: self.toggle_tool(ToolType.SELECT_RECT))
        self.tool_buttons['select_rect'].pack(fill=tk.X, padx=5, pady=2)
        
        self.tool_buttons['select_lasso'] = tk.Button(basic_frame, text="Select (Lasso)", relief=tk.RAISED,
                                                      command=lambda: self.toggle_tool(ToolType.SELECT_LASSO))
        self.tool_buttons['select_lasso'].pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Separator(basic_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(basic_frame, text="Clear All", command=self.clear_all).pack(fill=tk.X, padx=5, pady=2)
        
        # Element tools
        element_frame = ttk.LabelFrame(tool_frame, text="Elements")
        element_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Quick element buttons
        element_grid = ttk.Frame(element_frame)
        element_grid.pack(fill=tk.X, padx=5, pady=2)
        
        common_elements = ['H', 'C', 'N', 'O', 'F', 'P', 'S', 'Cl', 'Br', 'I']
        for i, element in enumerate(common_elements):
            btn_key = f'element_{element}'
            color = get_element_color(element)
            # Adjust text color for visibility
            text_color = 'white' if element in ['C', 'N', 'Br', 'I'] else 'black'
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
        
        # 2D Canvas
        canvas_frame = ttk.LabelFrame(left_frame, text="2D Editor")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas_2d = tk.Canvas(canvas_frame, bg='white', width=600, height=600)
        self.canvas_2d.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind canvas events
        self.canvas_2d.bind("<Button-1>", self.on_canvas_click)
        self.canvas_2d.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas_2d.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas_2d.bind("<Button-3>", self.on_right_click)
        
        # Right side - 3D Viewer
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 3D controls
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Reload 3D", command=self.update_3d_view).pack(side=tk.LEFT, padx=5)
        
        # Background color options
        ttk.Label(control_frame, text="Background:").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Black", command=lambda: self.set_3d_bg('#000000')).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="White", command=lambda: self.set_3d_bg('#FFFFFF')).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Gray", command=lambda: self.set_3d_bg('#808080')).pack(side=tk.LEFT, padx=2)
        
        # 3D Viewer
        viewer_frame = ttk.LabelFrame(right_frame, text="3D Viewer")
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for 3D
        self.fig_3d = plt.Figure(figsize=(6, 6), dpi=100)
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.setup_3d_view()
        
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, viewer_frame)
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready - No tool selected", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Element info label
        self.element_info = ttk.Label(self.root, text="", relief=tk.SUNKEN)
        self.element_info.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_3d_view(self):
        self.ax_3d.set_facecolor(self.bg_color_3d)
        # Remove axes and gridlines
        self.ax_3d.set_axis_off()
        self.ax_3d.grid(False)
        self.ax_3d.set_xticks([])
        self.ax_3d.set_yticks([])
        self.ax_3d.set_zticks([])
        
    def toggle_tool(self, tool_type, element=None, bond_type=None):
        # If clicking the current tool, deactivate it
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
        
        # Deactivate all tools first
        self.deactivate_all_tools()
        
        # Activate the new tool
        self.current_tool = tool_type
        
        # Update button appearance
        if tool_type == ToolType.DRAG:
            self.tool_buttons['drag'].config(relief=tk.SUNKEN, bg='lightblue')
        elif tool_type == ToolType.DELETE:
            self.tool_buttons['delete'].config(relief=tk.SUNKEN, bg='lightblue')
        elif tool_type == ToolType.SELECT_RECT:
            self.tool_buttons['select_rect'].config(relief=tk.SUNKEN, bg='lightblue')
        elif tool_type == ToolType.SELECT_LASSO:
            self.tool_buttons['select_lasso'].config(relief=tk.SUNKEN, bg='lightblue')
        elif tool_type == ToolType.CHARGE_POSITIVE:
            self.tool_buttons['charge_pos'].config(relief=tk.SUNKEN, bg='lightblue')
        elif tool_type == ToolType.CHARGE_NEGATIVE:
            self.tool_buttons['charge_neg'].config(relief=tk.SUNKEN, bg='lightblue')
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
    
    def update_element_info(self, element_symbol):
        try:
            element = getattr(pt, element_symbol)
            info = f"{element.name} ({element_symbol}) - Atomic #: {element.number}, Mass: {element.mass:.2f}"
            self.element_info.config(text=info)
        except:
            self.element_info.config(text=f"Element: {element_symbol}")
    
    def select_element_tool(self, element):
        self.toggle_tool(ToolType.ELEMENT, element=element)
    
    def select_bond_tool(self, bond_type):
        self.toggle_tool(ToolType.BOND, bond_type=bond_type)
        self.bond_start_atom = None
    
    def deactivate_all_tools(self):
        self.current_tool = ToolType.NONE
        self.bond_start_atom = None
        
        # Reset all button appearances
        for key, btn in self.tool_buttons.items():
            if key.startswith('element_'):
                element = key.replace('element_', '')
                color = get_element_color(element)
                text_color = 'white' if element in ['C', 'N', 'Br', 'I'] else 'black'
                btn.config(relief=tk.RAISED, bg=color, fg=text_color)
            else:
                btn.config(relief=tk.RAISED, bg='SystemButtonFace')
        
        self.element_info.config(text="")
        self.update_status_message()
    
    def update_status_message(self):
        if self.current_tool == ToolType.NONE:
            msg = "No tool selected"
        elif self.current_tool == ToolType.DRAG:
            msg = "Tool: Drag - Click and drag atoms to move them"
        elif self.current_tool == ToolType.DELETE:
            msg = "Tool: Delete - Click on atoms or bonds to delete"
        elif self.current_tool == ToolType.SELECT_RECT:
            msg = "Tool: Rectangle Selection - Drag to select atoms"
        elif self.current_tool == ToolType.SELECT_LASSO:
            msg = "Tool: Lasso Selection - Draw around atoms to select"
        elif self.current_tool == ToolType.ELEMENT:
            msg = f"Tool: Add {self.current_element} atom - Click to place"
        elif self.current_tool == ToolType.BOND:
            if self.bond_start_atom:
                msg = f"Tool: {self.current_bond_type.name} bond - Click second atom"
            else:
                msg = f"Tool: {self.current_bond_type.name} bond - Click first atom"
        elif self.current_tool == ToolType.CHARGE_POSITIVE:
            msg = "Tool: Add positive charge - Click on atoms"
        elif self.current_tool == ToolType.CHARGE_NEGATIVE:
            msg = "Tool: Add negative charge - Click on atoms"
        else:
            msg = "Ready"
        
        self.status_bar.config(text=msg)
    
    def on_canvas_click(self, event):
        x, y = event.x, event.y
        
        if self.current_tool == ToolType.NONE:
            return
        
        elif self.current_tool == ToolType.DRAG:
            clicked_atom = self.get_atom_at(x, y)
            if clicked_atom is not None:
                self.drag_atom = clicked_atom
                self.drag_start = (x, y)
        
        elif self.current_tool == ToolType.DELETE:
            self.delete_at(x, y)
        
        elif self.current_tool == ToolType.SELECT_RECT:
            self.selection_start = (x, y)
            self.selection_rect = self.canvas_2d.create_rectangle(x, y, x, y, outline='blue', dash=(5, 5))
        
        elif self.current_tool == ToolType.SELECT_LASSO:
            self.lasso_points = [(x, y)]
            if self.lasso_line:
                self.canvas_2d.delete(self.lasso_line)
        
        elif self.current_tool == ToolType.ELEMENT:
            clicked_atom = self.get_atom_at(x, y)
            if clicked_atom is None:
                self.create_atom(x, y)
        
        elif self.current_tool == ToolType.BOND:
            clicked_atom = self.get_atom_at(x, y)
            if clicked_atom is not None:
                if self.bond_start_atom is None:
                    self.bond_start_atom = clicked_atom
                    self.canvas_2d.itemconfig(self.atoms[clicked_atom].canvas_id, outline='green', width=3)
                    self.update_status_message()
                else:
                    if clicked_atom != self.bond_start_atom:
                        self.create_bond(self.bond_start_atom, clicked_atom)
                        self.adjust_bond_length(self.bond_start_atom, clicked_atom)
                    self.canvas_2d.itemconfig(self.atoms[self.bond_start_atom].canvas_id, outline='black', width=2)
                    self.bond_start_atom = None
                    self.update_status_message()
        
        elif self.current_tool == ToolType.CHARGE_POSITIVE:
            clicked_atom = self.get_atom_at(x, y)
            if clicked_atom is not None:
                self.atoms[clicked_atom].charge += 1
                self.update_atom_display(clicked_atom)
        
        elif self.current_tool == ToolType.CHARGE_NEGATIVE:
            clicked_atom = self.get_atom_at(x, y)
            if clicked_atom is not None:
                self.atoms[clicked_atom].charge -= 1
                self.update_atom_display(clicked_atom)
    
    def adjust_bond_length(self, atom1_id, atom2_id):
        """Adjust atom positions to maintain consistent bond length"""
        atom1 = self.atoms[atom1_id]
        atom2 = self.atoms[atom2_id]
        
        dx = atom2.x - atom1.x
        dy = atom2.y - atom1.y
        current_distance = math.sqrt(dx**2 + dy**2)
        
        if current_distance > 0 and abs(current_distance - self.bond_length) > 5:
            scale = self.bond_length / current_distance
            new_dx = dx * scale
            new_dy = dy * scale
            
            new_x = atom1.x + new_dx
            new_y = atom1.y + new_dy
            
            move_dx = new_x - atom2.x
            move_dy = new_y - atom2.y
            self.move_atom(atom2_id, move_dx, move_dy)
    
    def get_atom_at(self, x, y):
        """Find atom at given coordinates"""
        for atom_id, atom in self.atoms.items():
            distance = math.sqrt((atom.x - x)**2 + (atom.y - y)**2)
            if distance <= atom.radius:
                return atom_id
        return None
    
    def on_canvas_drag(self, event):
        x, y = event.x, event.y
        
        if self.current_tool == ToolType.DRAG and self.drag_atom is not None:
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            self.move_atom(self.drag_atom, dx, dy)
            self.drag_start = (x, y)
        
        elif self.current_tool == ToolType.SELECT_RECT and self.selection_rect:
            x0, y0 = self.selection_start
            self.canvas_2d.coords(self.selection_rect, x0, y0, x, y)
        
        elif self.current_tool == ToolType.SELECT_LASSO:
            self.lasso_points.append((x, y))
            if len(self.lasso_points) > 1:
                if self.lasso_line:
                    self.canvas_2d.delete(self.lasso_line)
                flat_points = [coord for point in self.lasso_points for coord in point]
                self.lasso_line = self.canvas_2d.create_line(*flat_points, fill='blue', dash=(5, 5))
    
    def on_canvas_release(self, event):
        if self.current_tool == ToolType.DRAG:
            self.drag_atom = None
            self.drag_start = None
        
        elif self.current_tool == ToolType.SELECT_RECT and self.selection_rect:
            self.select_atoms_in_rect()
            self.canvas_2d.delete(self.selection_rect)
            self.selection_rect = None
            self.selection_start = None
        
        elif self.current_tool == ToolType.SELECT_LASSO and self.lasso_line:
            self.select_atoms_in_lasso()
            self.canvas_2d.delete(self.lasso_line)
            self.lasso_line = None
            self.lasso_points = []
    
    def on_right_click(self, event):
        if self.bond_start_atom is not None:
            self.canvas_2d.itemconfig(self.atoms[self.bond_start_atom].canvas_id, outline='black', width=2)
            self.bond_start_atom = None
            self.update_status_message()
    
    def create_atom(self, x, y):
        atom_id = self.next_atom_id
        self.next_atom_id += 1
        
        atom = Atom(
            element=self.current_element,
            x=x,
            y=y,
            z=0,
            charge=0,
            id=atom_id,
            radius=self.atom_radius
        )
        
        # Draw atom on canvas
        color = get_element_color(atom.element)
        canvas_id = self.canvas_2d.create_oval(
            x - self.atom_radius, y - self.atom_radius,
            x + self.atom_radius, y + self.atom_radius,
            fill=color, outline='black', width=2
        )
        
        # Determine text color for visibility
        # White text for dark colors, black for light colors
        if atom.element in ['C', 'N', 'Br', 'I'] or color[1:3] < '60':
            text_color = 'white'
        else:
            text_color = 'black'
            
        text_id = self.canvas_2d.create_text(x, y, text=atom.element, 
                                            fill=text_color, font=('Arial', 14, 'bold'))
        
        atom.canvas_id = canvas_id
        atom.text_id = text_id
        self.atoms[atom_id] = atom
        
        return atom_id
    
    def create_bond(self, atom1_id, atom2_id):
        # Check if bond already exists
        for bond in self.bonds:
            if (bond.atom1_id == atom1_id and bond.atom2_id == atom2_id) or \
               (bond.atom1_id == atom2_id and bond.atom2_id == atom1_id):
                self.delete_bond(bond)
                break
        
        bond = Bond(atom1_id, atom2_id, self.current_bond_type)
        
        # Draw bond on canvas
        atom1 = self.atoms[atom1_id]
        atom2 = self.atoms[atom2_id]
        
        canvas_id = self.draw_bond(atom1, atom2, self.current_bond_type)
        
        bond.canvas_id = canvas_id
        self.bonds.append(bond)
        
        # Move bond behind atoms
        if isinstance(canvas_id, tuple):
            for cid in canvas_id:
                self.canvas_2d.tag_lower(cid)
        else:
            if canvas_id:
                self.canvas_2d.tag_lower(canvas_id)
    
    def draw_bond(self, atom1, atom2, bond_type):
        # Calculate bond endpoints
        dx = atom2.x - atom1.x
        dy = atom2.y - atom1.y
        length = math.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return None
        
        # Unit vector
        ux = dx / length
        uy = dy / length
        
        # Shorten bond by atom radius
        x1 = atom1.x + ux * self.atom_radius
        y1 = atom1.y + uy * self.atom_radius
        x2 = atom2.x - ux * self.atom_radius
        y2 = atom2.y - uy * self.atom_radius
        
        if bond_type == BondType.SINGLE:
            return self.canvas_2d.create_line(x1, y1, x2, y2, fill='black', width=3)
        
        elif bond_type == BondType.DOUBLE:
            offset = 5
            dx_perp = -uy * offset
            dy_perp = ux * offset
            
            id1 = self.canvas_2d.create_line(
                x1 + dx_perp, y1 + dy_perp,
                x2 + dx_perp, y2 + dy_perp,
                fill='black', width=2
            )
            id2 = self.canvas_2d.create_line(
                x1 - dx_perp, y1 - dy_perp,
                x2 - dx_perp, y2 - dy_perp,
                fill='black', width=2
            )
            return (id1, id2)
        
        elif bond_type == BondType.TRIPLE:
            offset = 6
            dx_perp = -uy * offset
            dy_perp = ux * offset
            
            id1 = self.canvas_2d.create_line(x1, y1, x2, y2, fill='black', width=2)
            id2 = self.canvas_2d.create_line(
                x1 + dx_perp, y1 + dy_perp,
                x2 + dx_perp, y2 + dy_perp,
                fill='black', width=2
            )
            id3 = self.canvas_2d.create_line(
                x1 - dx_perp, y1 - dy_perp,
                x2 - dx_perp, y2 - dy_perp,
                fill='black', width=2
            )
            return (id1, id2, id3)
        
        elif bond_type == BondType.WEDGE:
            points = self.calculate_wedge_points(x1, y1, x2, y2)
            return self.canvas_2d.create_polygon(points, fill='black')
        
        elif bond_type == BondType.HASH:
            return self.draw_hash_bond(x1, y1, x2, y2)
    
    def calculate_wedge_points(self, x1, y1, x2, y2):
        angle = math.atan2(y2 - y1, x2 - x1)
        perpendicular = angle + math.pi / 2
        width = 10
        
        return [
            x1, y1,
            x2 + width * math.cos(perpendicular), y2 + width * math.sin(perpendicular),
            x2 - width * math.cos(perpendicular), y2 - width * math.sin(perpendicular)
        ]
    
    def draw_hash_bond(self, x1, y1, x2, y2):
        num_lines = 6
        lines = []
        
        for i in range(num_lines):
            t = i / (num_lines - 1)
            xi = x1 + t * (x2 - x1)
            yi = y1 + t * (y2 - y1)
            
            angle = math.atan2(y2 - y1, x2 - x1) + math.pi / 2
            width = 3 + t * 7
            
            dx = width * math.cos(angle)
            dy = width * math.sin(angle)
            
            line_id = self.canvas_2d.create_line(
                xi - dx, yi - dy,
                xi + dx, yi + dy,
                fill='black', width=2
            )
            lines.append(line_id)
        
        return tuple(lines)
    
    def delete_bond(self, bond):
        if isinstance(bond.canvas_id, tuple):
            for cid in bond.canvas_id:
                self.canvas_2d.delete(cid)
        else:
            if bond.canvas_id:
                self.canvas_2d.delete(bond.canvas_id)
        self.bonds.remove(bond)
    
    def move_atom(self, atom_id, dx, dy):
        if atom_id not in self.atoms:
            return
        
        atom = self.atoms[atom_id]
        atom.x += dx
        atom.y += dy
        
        # Move atom visual
        self.canvas_2d.move(atom.canvas_id, dx, dy)
        self.canvas_2d.move(atom.text_id, dx, dy)
        
        # Update connected bonds
        self.update_bonds_for_atom(atom_id)
    
    def update_bonds_for_atom(self, atom_id):
        for bond in self.bonds:
            if bond.atom1_id == atom_id or bond.atom2_id == atom_id:
                # Delete old bond visual
                if isinstance(bond.canvas_id, tuple):
                    for cid in bond.canvas_id:
                        self.canvas_2d.delete(cid)
                else:
                    if bond.canvas_id:
                        self.canvas_2d.delete(bond.canvas_id)
                
                # Redraw bond
                atom1 = self.atoms[bond.atom1_id]
                atom2 = self.atoms[bond.atom2_id]
                
                canvas_id = self.draw_bond(atom1, atom2, bond.bond_type)
                bond.canvas_id = canvas_id
                
                if canvas_id:
                    if isinstance(canvas_id, tuple):
                        for cid in canvas_id:
                            self.canvas_2d.tag_lower(cid)
                    else:
                        self.canvas_2d.tag_lower(canvas_id)
    
    def delete_at(self, x, y):
        # Check for atom
        atom_id = self.get_atom_at(x, y)
        if atom_id is not None:
            self.delete_atom(atom_id)
            return
        
        # Check for bond
        for bond in self.bonds[:]:
            atom1 = self.atoms[bond.atom1_id]
            atom2 = self.atoms[bond.atom2_id]
            
            if self.point_near_line(x, y, atom1.x, atom1.y, atom2.x, atom2.y, 10):
                self.delete_bond(bond)
                return
    
    def point_near_line(self, px, py, x1, y1, x2, y2, threshold):
        line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_len == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2) < threshold
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len**2))
        projection_x = x1 + t * (x2 - x1)
        projection_y = y1 + t * (y2 - y1)
        
        distance = math.sqrt((px - projection_x)**2 + (py - projection_y)**2)
        return distance < threshold
    
    def delete_atom(self, atom_id):
        if atom_id not in self.atoms:
            return
        
        atom = self.atoms[atom_id]
        
        # Delete atom visual
        self.canvas_2d.delete(atom.canvas_id)
        self.canvas_2d.delete(atom.text_id)
        
        # Delete connected bonds
        bonds_to_remove = []
        for bond in self.bonds:
            if bond.atom1_id == atom_id or bond.atom2_id == atom_id:
                if isinstance(bond.canvas_id, tuple):
                    for cid in bond.canvas_id:
                        self.canvas_2d.delete(cid)
                else:
                    if bond.canvas_id:
                        self.canvas_2d.delete(bond.canvas_id)
                bonds_to_remove.append(bond)
        
        for bond in bonds_to_remove:
            self.bonds.remove(bond)
        
        del self.atoms[atom_id]
        
        if atom_id in self.selected_atoms:
            self.selected_atoms.remove(atom_id)
    
    def update_atom_display(self, atom_id):
        if atom_id not in self.atoms:
            return
        
        atom = self.atoms[atom_id]
        
        # Update text with charge
        charge_text = ""
        if atom.charge > 0:
            charge_text = f"{atom.charge}+" if atom.charge > 1 else "+"
        elif atom.charge < 0:
            charge_text = f"{abs(atom.charge)}-" if atom.charge < -1 else "-"
        
        display_text = f"{atom.element}{charge_text}"
        
        # Maintain text color based on background
        color = get_element_color(atom.element)
        if atom.element in ['C', 'N', 'Br', 'I'] or color[1:3] < '60':
            text_color = 'white'
        else:
            text_color = 'black'
            
        self.canvas_2d.itemconfig(atom.text_id, text=display_text, fill=text_color)
    
    def select_atoms_in_rect(self):
        if not self.selection_start:
            return
        
        x1, y1 = self.selection_start
        coords = self.canvas_2d.coords(self.selection_rect)
        if len(coords) >= 4:
            x2, y2 = coords[2], coords[3]
            
            self.clear_selection()
            
            for atom_id, atom in self.atoms.items():
                if min(x1, x2) <= atom.x <= max(x1, x2) and \
                   min(y1, y2) <= atom.y <= max(y1, y2):
                    self.selected_atoms.add(atom_id)
                    self.canvas_2d.itemconfig(atom.canvas_id, outline='blue', width=3)
    
    def select_atoms_in_lasso(self):
        if len(self.lasso_points) < 3:
            return
        
        self.clear_selection()
        
        for atom_id, atom in self.atoms.items():
            if self.point_in_polygon(atom.x, atom.y, self.lasso_points):
                self.selected_atoms.add(atom_id)
                self.canvas_2d.itemconfig(atom.canvas_id, outline='blue', width=3)
    
    def point_in_polygon(self, x, y, polygon):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def clear_selection(self):
        for atom_id in self.selected_atoms:
            if atom_id in self.atoms:
                self.canvas_2d.itemconfig(self.atoms[atom_id].canvas_id, outline='black', width=2)
        self.selected_atoms.clear()
    
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
    
    def draw_3d_bicolor_cylinder(self, p1, p2, color1, color2, radius=0.15):
        """Draw a cylinder with two colors (half and half)"""
        v = p2 - p1
        height = np.linalg.norm(v)
        if height == 0:
            return
        
        v = v / height
        midpoint = (p1 + p2) / 2
        
        # Draw first half
        self.draw_3d_cylinder_segment(p1, midpoint, radius, color1)
        # Draw second half
        self.draw_3d_cylinder_segment(midpoint, p2, radius, color2)
    
    def draw_3d_cylinder_segment(self, p1, p2, radius, color):
        """Draw a cylinder segment between two points"""
        v = p2 - p1
        height = np.linalg.norm(v)
        if height == 0:
            return
        
        v = v / height
        
        # Create rotation matrix
        not_v = np.array([1, 0, 0])
        if np.allclose(v, not_v):
            not_v = np.array([0, 1, 0])
        
        n1 = np.cross(v, not_v)
        n1 = n1 / np.linalg.norm(n1)
        n2 = np.cross(v, n1)
        
        # Generate cylinder
        theta = np.linspace(0, 2*np.pi, 20)
        z = np.linspace(0, height, 10)
        theta_grid, z_grid = np.meshgrid(theta, z)
        
        x_cyl = radius * np.cos(theta_grid)
        y_cyl = radius * np.sin(theta_grid)
        
        # Transform points
        points = np.zeros((10, 20, 3))
        for i in range(10):
            for j in range(20):
                point = p1 + z_grid[i, j] * v + x_cyl[i, j] * n1 + y_cyl[i, j] * n2
                points[i, j] = point
        
        self.ax_3d.plot_surface(
            points[:,:,0], points[:,:,1], points[:,:,2],
            color=color, alpha=1.0, shade=False, edgecolor='none', linewidth=0
        )
    
    def update_3d_view(self):
        self.ax_3d.clear()
        self.setup_3d_view()
        
        if not self.atoms:
            self.canvas_3d.draw()
            return
        
        # Calculate 3D positions
        self.calculate_3d_positions()
        
        # Standard atom radius for 3D view
        atom_3d_radius = 0.5
        
        # Draw atoms as smooth spheres
        for atom_id, atom in self.atoms.items():
            color = get_element_color(atom.element)
            
            # Create smooth sphere
            u = np.linspace(0, 2 * np.pi, 30)
            v = np.linspace(0, np.pi, 30)
            x = atom_3d_radius * np.outer(np.cos(u), np.sin(v)) + atom.x / 100
            y = atom_3d_radius * np.outer(np.sin(u), np.sin(v)) + atom.y / 100
            z = atom_3d_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + atom.z
            
            self.ax_3d.plot_surface(x, y, z, color=color, alpha=1.0,
                                   shade=False, edgecolor='none', linewidth=0)
        
        # Draw bonds with element colors
        for bond in self.bonds:
            atom1 = self.atoms[bond.atom1_id]
            atom2 = self.atoms[bond.atom2_id]
            
            p1 = np.array([atom1.x / 100, atom1.y / 100, atom1.z])
            p2 = np.array([atom2.x / 100, atom2.y / 100, atom2.z])
            
            # Get element colors
            color1 = get_element_color(atom1.element)
            color2 = get_element_color(atom2.element)
            
            # Calculate direction vector
            direction = p2 - p1
            length = np.linalg.norm(direction)
            
            if length > 0:
                unit_dir = direction / length
                p1_adjusted = p1 + unit_dir * atom_3d_radius * 0.8
                p2_adjusted = p2 - unit_dir * atom_3d_radius * 0.8
                
                if bond.bond_type == BondType.SINGLE:
                    self.draw_3d_bicolor_cylinder(p1_adjusted, p2_adjusted, color1, color2, radius=0.15)
                
                elif bond.bond_type == BondType.DOUBLE:
                    offset = 0.15
                    perp = np.array([-unit_dir[1], unit_dir[0], 0]) * offset
                    self.draw_3d_bicolor_cylinder(p1_adjusted + perp, p2_adjusted + perp, color1, color2, radius=0.10)
                    self.draw_3d_bicolor_cylinder(p1_adjusted - perp, p2_adjusted - perp, color1, color2, radius=0.10)
                
                elif bond.bond_type == BondType.TRIPLE:
                    offset = 0.20
                    perp = np.array([-unit_dir[1], unit_dir[0], 0]) * offset
                    self.draw_3d_bicolor_cylinder(p1_adjusted, p2_adjusted, color1, color2, radius=0.08)
                    self.draw_3d_bicolor_cylinder(p1_adjusted + perp, p2_adjusted + perp, color1, color2, radius=0.08)
                    self.draw_3d_bicolor_cylinder(p1_adjusted - perp, p2_adjusted - perp, color1, color2, radius=0.08)
                
                elif bond.bond_type == BondType.WEDGE:
                    self.draw_3d_bicolor_cylinder(p1_adjusted, p2_adjusted, color1, color2, radius=0.25)
                
                elif bond.bond_type == BondType.HASH:
                    # Multiple segments for hash
                    segments = 5
                    for i in range(segments):
                        t1 = i / segments
                        t2 = (i + 0.5) / segments
                        seg_p1 = p1_adjusted + (p2_adjusted - p1_adjusted) * t1
                        seg_p2 = p1_adjusted + (p2_adjusted - p1_adjusted) * t2
                        
                        # Interpolate colors
                        if i % 2 == 0:
                            self.draw_3d_cylinder_segment(seg_p1, seg_p2, 0.12, color1 if i < segments/2 else color2)
        
        # Set equal aspect ratio
        max_range = 6
        self.ax_3d.set_xlim([-max_range, max_range])
        self.ax_3d.set_ylim([-max_range, max_range])
        self.ax_3d.set_zlim([-max_range, max_range])
        
        # Set viewing angle
        self.ax_3d.view_init(elev=20, azim=45)
        
        self.canvas_3d.draw()
    
    def calculate_3d_positions(self):
        for atom_id, atom in self.atoms.items():
            atom.z = 0
        
        for bond in self.bonds:
            if bond.bond_type == BondType.WEDGE:
                self.atoms[bond.atom2_id].z = 2.0
            elif bond.bond_type == BondType.HASH:
                self.atoms[bond.atom2_id].z = -2.0
    
    def show_periodic_table(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Periodic Table")
        dialog.geometry("1200x700")
        
        # Create main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Periodic table layout
        elements_layout = [
            ['H', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'He'],
            ['Li', 'Be', '', '', '', '', '', '', '', '', '', '', 'B', 'C', 'N', 'O', 'F', 'Ne'],
            ['Na', 'Mg', '', '', '', '', '', '', '', '', '', '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],
            ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],
            ['Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],
            ['Cs', 'Ba', '*', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'],
            ['Fr', 'Ra', '**', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'],
        ]
        
        # Lanthanides and Actinides
        lanthanides = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        actinides = ['Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr']
        
        # Main periodic table
        for row_idx, row in enumerate(elements_layout):
            for col_idx, element_symbol in enumerate(row):
                if element_symbol and element_symbol not in ['*', '**']:
                    try:
                        element = getattr(pt, element_symbol)
                        color = get_element_color(element_symbol)
                        
                        # Determine text color
                        if element_symbol in ['C', 'N', 'Br', 'I'] or (len(color) == 7 and color[1:3] < '60'):
                            text_color = 'white'
                        else:
                            text_color = 'black'
                        
                        btn = tk.Button(main_frame,
                                      text=f"{element_symbol}\n{element.number}",
                                      width=4, height=2,
                                      bg=color, fg=text_color,
                                      relief=tk.RAISED,
                                      command=lambda e=element_symbol: [self.select_element_tool(e), dialog.destroy()])
                        btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                    except:
                        pass
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=8, column=0, columnspan=18, sticky='ew', pady=10)
        
        # Add lanthanides
        ttk.Label(main_frame, text="*Lanthanides:", font=('Arial', 10, 'bold')).grid(row=9, column=0, columnspan=3, sticky='w')
        for idx, element_symbol in enumerate(lanthanides):
            try:
                element = getattr(pt, element_symbol)
                color = get_element_color(element_symbol)
                
                # Determine text color
                if len(color) == 7 and color[1:3] < '60':
                    text_color = 'white'
                else:
                    text_color = 'black'
                
                btn = tk.Button(main_frame,
                              text=f"{element_symbol}\n{element.number}",
                              width=4, height=2,
                              bg=color, fg=text_color,
                              relief=tk.RAISED,
                              command=lambda e=element_symbol: [self.select_element_tool(e), dialog.destroy()])
                btn.grid(row=9, column=idx+3, padx=1, pady=1)
            except:
                pass
        
        # Add actinides
        ttk.Label(main_frame, text="**Actinides:", font=('Arial', 10, 'bold')).grid(row=10, column=0, columnspan=3, sticky='w')
        for idx, element_symbol in enumerate(actinides):
            try:
                element = getattr(pt, element_symbol)
                color = get_element_color(element_symbol)
                
                # Determine text color
                if len(color) == 7 and color[1:3] < '60':
                    text_color = 'white'
                else:
                    text_color = 'black'
                
                btn = tk.Button(main_frame,
                              text=f"{element_symbol}\n{element.number}",
                              width=4, height=2,
                              bg=color, fg=text_color,
                              relief=tk.RAISED,
                              command=lambda e=element_symbol: [self.select_element_tool(e), dialog.destroy()])
                btn.grid(row=10, column=idx+3, padx=1, pady=1)
            except:
                pass

def main():
    root = tk.Tk()
    app = MolecularEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()

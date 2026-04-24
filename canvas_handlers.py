"""
Canvas event handlers
"""

import math
from components import ToolType
from canvas_operations import (
    get_atom_at, create_atom, create_bond, delete_atom,
    move_atom, update_atom_display, adjust_bond_length
)

def handle_canvas_click(editor, event):
    x, y = event.x, event.y
    
    if editor.current_tool == ToolType.NONE:
        return
    
    elif editor.current_tool == ToolType.DRAG:
        clicked_atom = get_atom_at(editor, x, y)
        if clicked_atom is not None:
            editor.drag_atom = clicked_atom
            editor.drag_start = (x, y)
    
    elif editor.current_tool == ToolType.DELETE:
        delete_at(editor, x, y)
    
    elif editor.current_tool == ToolType.SELECT_RECT:
        editor.selection_start = (x, y)
        editor.selection_rect = editor.canvas_2d.create_rectangle(
            x, y, x, y, outline='blue', dash=(5, 5)
        )
    
    elif editor.current_tool == ToolType.SELECT_LASSO:
        editor.lasso_points = [(x, y)]
        if editor.lasso_line:
            editor.canvas_2d.delete(editor.lasso_line)
    
    elif editor.current_tool == ToolType.ELEMENT:
        clicked_atom = get_atom_at(editor, x, y)
        if clicked_atom is None:
            create_atom(editor, x, y)
    
    elif editor.current_tool == ToolType.BOND:
        clicked_atom = get_atom_at(editor, x, y)
        if clicked_atom is not None:
            if editor.bond_start_atom is None:
                editor.bond_start_atom = clicked_atom
                editor.canvas_2d.itemconfig(
                    editor.atoms[clicked_atom].canvas_id,
                    outline='green', width=3
                )
                editor.update_status_message()
            else:
                if clicked_atom != editor.bond_start_atom:
                    create_bond(editor, editor.bond_start_atom, clicked_atom)
                    adjust_bond_length(editor, editor.bond_start_atom, clicked_atom)
                editor.canvas_2d.itemconfig(
                    editor.atoms[editor.bond_start_atom].canvas_id,
                    outline='black', width=2
                )
                editor.bond_start_atom = None
                editor.update_status_message()
    
    elif editor.current_tool == ToolType.CHARGE_POSITIVE:
        clicked_atom = get_atom_at(editor, x, y)
        if clicked_atom is not None:
            editor.atoms[clicked_atom].charge += 1
            update_atom_display(editor, clicked_atom)
    
    elif editor.current_tool == ToolType.CHARGE_NEGATIVE:
        clicked_atom = get_atom_at(editor, x, y)
        if clicked_atom is not None:
            editor.atoms[clicked_atom].charge -= 1
            update_atom_display(editor, clicked_atom)

def handle_canvas_drag(editor, event):
    x, y = event.x, event.y
    
    if editor.current_tool == ToolType.DRAG and editor.drag_atom is not None:
        dx = x - editor.drag_start[0]
        dy = y - editor.drag_start[1]
        move_atom(editor, editor.drag_atom, dx, dy)
        editor.drag_start = (x, y)
    
    elif editor.current_tool == ToolType.SELECT_RECT and editor.selection_rect:
        x0, y0 = editor.selection_start
        editor.canvas_2d.coords(editor.selection_rect, x0, y0, x, y)
    
    elif editor.current_tool == ToolType.SELECT_LASSO:
        editor.lasso_points.append((x, y))
        if len(editor.lasso_points) > 1:
            if editor.lasso_line:
                editor.canvas_2d.delete(editor.lasso_line)
            flat_points = [coord for point in editor.lasso_points for coord in point]
            editor.lasso_line = editor.canvas_2d.create_line(
                *flat_points, fill='blue', dash=(5, 5)
            )

def handle_canvas_release(editor, event):
    if editor.current_tool == ToolType.DRAG:
        editor.drag_atom = None
        editor.drag_start = None
    
    elif editor.current_tool == ToolType.SELECT_RECT and editor.selection_rect:
        select_atoms_in_rect(editor)
        editor.canvas_2d.delete(editor.selection_rect)
        editor.selection_rect = None
        editor.selection_start = None
    
    elif editor.current_tool == ToolType.SELECT_LASSO and editor.lasso_line:
        select_atoms_in_lasso(editor)
        editor.canvas_2d.delete(editor.lasso_line)
        editor.lasso_line = None
        editor.lasso_points = []

def handle_right_click(editor, event):
    if editor.bond_start_atom is not None:
        editor.canvas_2d.itemconfig(
            editor.atoms[editor.bond_start_atom].canvas_id,
            outline='black', width=2
        )
        editor.bond_start_atom = None
        editor.update_status_message()

def delete_at(editor, x, y):
    """Delete atom or bond at position"""
    atom_id = get_atom_at(editor, x, y)
    if atom_id is not None:
        delete_atom(editor, atom_id)
        return
    
    # Check for bond
    for bond in editor.bonds[:]:
        atom1 = editor.atoms[bond.atom1_id]
        atom2 = editor.atoms[bond.atom2_id]
        
        if point_near_line(x, y, atom1.x, atom1.y, atom2.x, atom2.y, 10):
            from canvas_operations import delete_bond
            delete_bond(editor, bond)
            return

def point_near_line(px, py, x1, y1, x2, y2, threshold):
    """Check if point is near line segment"""
    line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if line_len == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2) < threshold
    
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len**2))
    projection_x = x1 + t * (x2 - x1)
    projection_y = y1 + t * (y2 - y1)
    
    distance = math.sqrt((px - projection_x)**2 + (py - projection_y)**2)
    return distance < threshold

def select_atoms_in_rect(editor):
    """Select atoms within rectangle"""
    if not editor.selection_start:
        return
    
    x1, y1 = editor.selection_start
    coords = editor.canvas_2d.coords(editor.selection_rect)
    if len(coords) >= 4:
        x2, y2 = coords[2], coords[3]
        
        clear_selection(editor)
        
        for atom_id, atom in editor.atoms.items():
            if min(x1, x2) <= atom.x <= max(x1, x2) and \
               min(y1, y2) <= atom.y <= max(y1, y2):
                editor.selected_atoms.add(atom_id)
                editor.canvas_2d.itemconfig(atom.canvas_id, outline='blue', width=3)

def select_atoms_in_lasso(editor):
    """Select atoms within lasso"""
    if len(editor.lasso_points) < 3:
        return
    
    clear_selection(editor)
    
    for atom_id, atom in editor.atoms.items():
        if point_in_polygon(atom.x, atom.y, editor.lasso_points):
            editor.selected_atoms.add(atom_id)
            editor.canvas_2d.itemconfig(atom.canvas_id, outline='blue', width=3)

def point_in_polygon(x, y, polygon):
    """Check if point is inside polygon"""
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

def clear_selection(editor):
    """Clear atom selection"""
    for atom_id in editor.selected_atoms:
        if atom_id in editor.atoms:
            editor.canvas_2d.itemconfig(
                editor.atoms[atom_id].canvas_id,
                outline='black', width=2
            )
    editor.selected_atoms.clear()
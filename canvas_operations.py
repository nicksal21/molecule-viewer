"""
Canvas operations for 2D editor
"""

import math
from components import Atom, Bond
from element_data import get_element_color, should_use_white_text

def get_atom_at(editor, x, y):
    """Find atom at given coordinates"""
    for atom_id, atom in editor.atoms.items():
        distance = math.sqrt((atom.x - x)**2 + (atom.y - y)**2)
        if distance <= atom.radius:
            return atom_id
    return None

def create_atom(editor, x, y):
    """Create a new atom at specified position"""
    from element_data import get_element_color, should_use_white_text, get_element_radius_2d
    
    atom_id = editor.next_atom_id
    editor.next_atom_id += 1
    
    radius = get_element_radius_2d(editor.current_element)
    
    atom = Atom(
        element=editor.current_element,
        x=x,
        y=y,
        z=0,
        charge=0,
        id=atom_id,
        radius=radius
    )
    
    # Draw atom on canvas
    color = get_element_color(atom.element)
    canvas_id = editor.canvas_2d.create_oval(
        x - radius, y - radius,
        x + radius, y + radius,
        fill=color, outline='black', width=2
    )
    
    # Determine text color
    text_color = 'white' if should_use_white_text(atom.element, color) else 'black'
    
    text_id = editor.canvas_2d.create_text(
        x, y, text=atom.element,
        fill=text_color, font=('Arial', 14, 'bold')
    )
    
    atom.canvas_id = canvas_id
    atom.text_id = text_id
    editor.atoms[atom_id] = atom
    
    return atom_id

def create_bond(editor, atom1_id, atom2_id):
    """Create a bond between two atoms"""
    # Check if bond already exists
    for bond in editor.bonds:
        if (bond.atom1_id == atom1_id and bond.atom2_id == atom2_id) or \
           (bond.atom1_id == atom2_id and bond.atom2_id == atom1_id):
            delete_bond(editor, bond)
            break
    
    bond = Bond(atom1_id, atom2_id, editor.current_bond_type)
    
    atom1 = editor.atoms[atom1_id]
    atom2 = editor.atoms[atom2_id]
    
    canvas_id = draw_bond(editor, atom1, atom2, editor.current_bond_type)
    
    bond.canvas_id = canvas_id
    editor.bonds.append(bond)
    
    # Move bond behind atoms
    if isinstance(canvas_id, tuple):
        for cid in canvas_id:
            editor.canvas_2d.tag_lower(cid)
    else:
        if canvas_id:
            editor.canvas_2d.tag_lower(canvas_id)

def draw_bond(editor, atom1, atom2, bond_type):
    """Draw a bond on the canvas"""
    from components import BondType
    
    dx = atom2.x - atom1.x
    dy = atom2.y - atom1.y
    length = math.sqrt(dx**2 + dy**2)
    
    if length == 0:
        return None
    
    ux = dx / length
    uy = dy / length
    
    # Use actual atom radii for proper bond endpoints
    x1 = atom1.x + ux * atom1.radius
    y1 = atom1.y + uy * atom1.radius
    x2 = atom2.x - ux * atom2.radius
    y2 = atom2.y - uy * atom2.radius
    
    if bond_type == BondType.SINGLE:
        return editor.canvas_2d.create_line(x1, y1, x2, y2, fill='black', width=3)
    
    elif bond_type == BondType.DOUBLE:
        offset = 5
        dx_perp = -uy * offset
        dy_perp = ux * offset
        
        id1 = editor.canvas_2d.create_line(
            x1 + dx_perp, y1 + dy_perp,
            x2 + dx_perp, y2 + dy_perp,
            fill='black', width=2
        )
        id2 = editor.canvas_2d.create_line(
            x1 - dx_perp, y1 - dy_perp,
            x2 - dx_perp, y2 - dy_perp,
            fill='black', width=2
        )
        return (id1, id2)
    
    elif bond_type == BondType.TRIPLE:
        offset = 6
        dx_perp = -uy * offset
        dy_perp = ux * offset
        
        id1 = editor.canvas_2d.create_line(x1, y1, x2, y2, fill='black', width=2)
        id2 = editor.canvas_2d.create_line(
            x1 + dx_perp, y1 + dy_perp,
            x2 + dx_perp, y2 + dy_perp,
            fill='black', width=2
        )
        id3 = editor.canvas_2d.create_line(
            x1 - dx_perp, y1 - dy_perp,
            x2 - dx_perp, y2 - dy_perp,
            fill='black', width=2
        )
        return (id1, id2, id3)
    
    elif bond_type == BondType.WEDGE:
        angle = math.atan2(y2 - y1, x2 - x1)
        perpendicular = angle + math.pi / 2
        width = 10
        
        points = [
            x1, y1,
            x2 + width * math.cos(perpendicular), y2 + width * math.sin(perpendicular),
            x2 - width * math.cos(perpendicular), y2 - width * math.sin(perpendicular)
        ]
        return editor.canvas_2d.create_polygon(points, fill='black')
    
    elif bond_type == BondType.HASH:
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
            
            line_id = editor.canvas_2d.create_line(
                xi - dx, yi - dy,
                xi + dx, yi + dy,
                fill='black', width=2
            )
            lines.append(line_id)
        
        return tuple(lines)

def delete_bond(editor, bond):
    """Delete a bond"""
    if isinstance(bond.canvas_id, tuple):
        for cid in bond.canvas_id:
            editor.canvas_2d.delete(cid)
    else:
        if bond.canvas_id:
            editor.canvas_2d.delete(bond.canvas_id)
    editor.bonds.remove(bond)

def delete_atom(editor, atom_id):
    """Delete an atom and its bonds"""
    if atom_id not in editor.atoms:
        return
    
    atom = editor.atoms[atom_id]
    
    # Delete atom visual
    editor.canvas_2d.delete(atom.canvas_id)
    editor.canvas_2d.delete(atom.text_id)
    
    # Delete connected bonds
    bonds_to_remove = []
    for bond in editor.bonds:
        if bond.atom1_id == atom_id or bond.atom2_id == atom_id:
            if isinstance(bond.canvas_id, tuple):
                for cid in bond.canvas_id:
                    editor.canvas_2d.delete(cid)
            else:
                if bond.canvas_id:
                    editor.canvas_2d.delete(bond.canvas_id)
            bonds_to_remove.append(bond)
    
    for bond in bonds_to_remove:
        editor.bonds.remove(bond)
    
    del editor.atoms[atom_id]
    
    if atom_id in editor.selected_atoms:
        editor.selected_atoms.remove(atom_id)

def move_atom(editor, atom_id, dx, dy):
    """Move an atom by dx, dy"""
    if atom_id not in editor.atoms:
        return
    
    atom = editor.atoms[atom_id]
    atom.x += dx
    atom.y += dy
    
    editor.canvas_2d.move(atom.canvas_id, dx, dy)
    editor.canvas_2d.move(atom.text_id, dx, dy)
    
    update_bonds_for_atom(editor, atom_id)

def update_bonds_for_atom(editor, atom_id):
    """Update bonds connected to an atom"""
    for bond in editor.bonds:
        if bond.atom1_id == atom_id or bond.atom2_id == atom_id:
            # Delete old bond visual
            if isinstance(bond.canvas_id, tuple):
                for cid in bond.canvas_id:
                    editor.canvas_2d.delete(cid)
            else:
                if bond.canvas_id:
                    editor.canvas_2d.delete(bond.canvas_id)
            
            # Redraw bond
            atom1 = editor.atoms[bond.atom1_id]
            atom2 = editor.atoms[bond.atom2_id]
            
            canvas_id = draw_bond(editor, atom1, atom2, bond.bond_type)
            bond.canvas_id = canvas_id
            
            if canvas_id:
                if isinstance(canvas_id, tuple):
                    for cid in canvas_id:
                        editor.canvas_2d.tag_lower(cid)
                else:
                    editor.canvas_2d.tag_lower(canvas_id)

def adjust_bond_length(editor, atom1_id, atom2_id):
    """Adjust atom positions to maintain consistent bond length based on atom sizes"""
    from element_data import get_element_radius_2d
    
    atom1 = editor.atoms[atom1_id]
    atom2 = editor.atoms[atom2_id]
    
    dx = atom2.x - atom1.x
    dy = atom2.y - atom1.y
    current_distance = math.sqrt(dx**2 + dy**2)
    
    if current_distance > 0:
        # Calculate minimum bond length based on atom radii
        radius1 = get_element_radius_2d(atom1.element)
        radius2 = get_element_radius_2d(atom2.element)
        min_bond_length = (radius1 + radius2) * 2.2  # 2.2x sum of radii for good spacing
        
        if current_distance < min_bond_length:
            scale = min_bond_length / current_distance
            new_dx = dx * scale
            new_dy = dy * scale
            
            new_x = atom1.x + new_dx
            new_y = atom1.y + new_dy
            
            move_dx = new_x - atom2.x
            move_dy = new_y - atom2.y
            move_atom(editor, atom2_id, move_dx, move_dy)

def update_atom_display(editor, atom_id):
    """Update atom text display with charge"""
    if atom_id not in editor.atoms:
        return
    
    atom = editor.atoms[atom_id]
    
    charge_text = ""
    if atom.charge > 0:
        charge_text = f"{atom.charge}+" if atom.charge > 1 else "+"
    elif atom.charge < 0:
        charge_text = f"{abs(atom.charge)}-" if atom.charge < -1 else "-"
    
    display_text = f"{atom.element}{charge_text}"
    
    color = get_element_color(atom.element)
    text_color = 'white' if should_use_white_text(atom.element, color) else 'black'
    
    editor.canvas_2d.itemconfig(atom.text_id, text=display_text, fill=text_color)
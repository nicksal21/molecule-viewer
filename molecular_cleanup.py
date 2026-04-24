"""
Molecular structure cleanup and optimization
"""

import math
import numpy as np
from element_data import get_element_radius_2d
from components import BondType
from vsepr_geometry import estimate_lone_pairs, get_vsepr_positions

def cleanup_structure(editor):
    """Clean up both 2D and 3D molecular structures"""
    # First, clean up 2D
    cleanup_2d_structure(editor)
    
    # Then update 3D based on cleaned 2D
    from viewer_3d import update_3d_view
    update_3d_view(editor)

def cleanup_2d_structure(editor):
    """Clean up 2D structure with proper angles and bond lengths"""
    if not editor.atoms:
        return
    
    # Step 1: Identify molecular fragments
    fragments = identify_fragments(editor)
    
    # Step 2: Process each fragment
    for fragment in fragments:
        if len(fragment) == 1:
            continue
            
        # Find the best central atom to start from
        central_atom_id = find_best_central_atom(editor, fragment)
        
        # Apply VSEPR-based 2D layout
        apply_2d_vsepr_layout(editor, central_atom_id, fragment)
    
    # Step 3: Align linear chains
    align_linear_chains(editor)
    
    # Step 4: Standardize bond lengths
    standardize_bond_lengths(editor)
    
    # Step 5: Redraw all atoms and bonds
    redraw_all_elements(editor)

def identify_fragments(editor):
    """Identify disconnected molecular fragments"""
    fragments = []
    visited = set()
    
    for atom_id in editor.atoms:
        if atom_id not in visited:
            fragment = set()
            to_visit = [atom_id]
            
            while to_visit:
                current = to_visit.pop()
                if current in visited:
                    continue
                    
                visited.add(current)
                fragment.add(current)
                
                # Find connected atoms
                for bond in editor.bonds:
                    if bond.atom1_id == current and bond.atom2_id not in visited:
                        to_visit.append(bond.atom2_id)
                    elif bond.atom2_id == current and bond.atom1_id not in visited:
                        to_visit.append(bond.atom1_id)
            
            fragments.append(fragment)
    
    return fragments

def find_best_central_atom(editor, fragment):
    """Find the atom with the most connections in a fragment"""
    max_connections = 0
    best_atom = None
    
    for atom_id in fragment:
        connections = 0
        for bond in editor.bonds:
            if bond.atom1_id == atom_id or bond.atom2_id == atom_id:
                connections += 1
        
        if connections > max_connections:
            max_connections = connections
            best_atom = atom_id
    
    return best_atom if best_atom else list(fragment)[0]

def apply_2d_vsepr_layout(editor, central_atom_id, fragment):
    """Apply VSEPR-based layout in 2D without forcing 45-degree angles"""
    if central_atom_id not in editor.atoms:
        return
    
    processed = {central_atom_id}
    to_process = [(central_atom_id, None)]
    
    while to_process:
        current_id, parent_id = to_process.pop(0)
        current_atom = editor.atoms[current_id]
        
        # Get connected atoms
        connected = []
        bond_types = {}  # Track bond types
        for bond in editor.bonds:
            if bond.atom1_id == current_id and bond.atom2_id != parent_id:
                connected.append(bond.atom2_id)
                bond_types[bond.atom2_id] = bond.bond_type
            elif bond.atom2_id == current_id and bond.atom1_id != parent_id:
                connected.append(bond.atom1_id)
                bond_types[bond.atom1_id] = bond.bond_type
        
        # Filter out already processed atoms
        new_connected = [aid for aid in connected if aid not in processed]
        
        if new_connected:
            # For double and triple bonds, preserve existing angles
            preserve_angles = {}
            for atom_id in new_connected:
                if atom_id in bond_types:
                    bond_type = bond_types[atom_id]
                    if bond_type in [BondType.DOUBLE, BondType.TRIPLE]:
                        # Calculate current angle
                        target_atom = editor.atoms[atom_id]
                        current_angle = math.atan2(
                            target_atom.y - current_atom.y,
                            target_atom.x - current_atom.x
                        )
                        preserve_angles[atom_id] = current_angle
            
            # Calculate ideal angles for atoms without preserved angles
            num_bonds = len(connected)
            lone_pairs = estimate_lone_pairs(current_atom.element, num_bonds)
            
            # Get ideal 2D angles
            angles = get_2d_angles(num_bonds, lone_pairs, parent_id is not None)
            
            # Apply angles
            if parent_id and parent_id in editor.atoms:
                parent_atom = editor.atoms[parent_id]
                base_angle = math.atan2(
                    current_atom.y - parent_atom.y,
                    current_atom.x - parent_atom.x
                )
            else:
                base_angle = 0
            
            # Position connected atoms
            angle_index = 0
            for atom_id in new_connected:
                if atom_id in editor.atoms:
                    # Use preserved angle for double/triple bonds
                    if atom_id in preserve_angles:
                        angle = preserve_angles[atom_id]
                    else:
                        angle = base_angle + angles[angle_index] if angle_index < len(angles) else base_angle
                        angle_index += 1
                    
                    # Calculate ideal bond length
                    from element_data import get_element_radius_2d
                    radius1 = get_element_radius_2d(current_atom.element)
                    radius2 = get_element_radius_2d(editor.atoms[atom_id].element)
                    bond_length = (radius1 + radius2) * 2.0
                    
                    # Position atom
                    editor.atoms[atom_id].x = current_atom.x + bond_length * math.cos(angle)
                    editor.atoms[atom_id].y = current_atom.y + bond_length * math.sin(angle)
                    
                    processed.add(atom_id)
                    to_process.append((atom_id, current_id))

def get_2d_angles(num_bonds, lone_pairs, has_parent):
    """Get ideal 2D angles for molecular geometry"""
    steric_number = num_bonds + lone_pairs
    
    if has_parent:
        num_bonds -= 1  # One bond is to parent
    
    if num_bonds == 0:
        return []
    elif num_bonds == 1:
        if steric_number == 2:
            return [math.pi]  # Linear: 180°
        elif steric_number == 3:
            return [math.radians(120)]  # Bent from trigonal
        elif steric_number == 4:
            return [math.radians(109.5)]  # From tetrahedral
    elif num_bonds == 2:
        if steric_number == 3:
            return [math.radians(120), math.radians(-120)]  # Trigonal planar
        elif steric_number == 4:
            if lone_pairs == 1:
                return [math.radians(107), math.radians(-107)]  # Pyramidal
            else:
                return [math.radians(109.5), math.radians(-109.5)]  # Tetrahedral
    elif num_bonds == 3:
        if steric_number == 4:
            return [0, math.radians(120), math.radians(-120)]  # Trigonal planar projection
        elif steric_number == 5:
            return [0, math.radians(120), math.radians(-120)]  # Equatorial positions
    
    # Default: distribute evenly
    angles = []
    for i in range(num_bonds):
        angles.append(2 * math.pi * i / num_bonds)
    return angles

def align_linear_chains(editor):
    """Align atoms that should be linear"""
    for atom_id in editor.atoms:
        connected = get_connected_atoms_list(editor, atom_id)
        
        if len(connected) == 2:
            # Check if this should be linear
            atom = editor.atoms[atom_id]
            if should_be_linear(atom.element, len(connected)):
                # Align the three atoms
                atom1 = editor.atoms[connected[0]]
                atom2 = editor.atoms[connected[1]]
                
                # Calculate midpoint
                mid_x = (atom1.x + atom2.x) / 2
                mid_y = (atom1.y + atom2.y) / 2
                
                # Move central atom to midpoint
                atom.x = mid_x
                atom.y = mid_y

def should_be_linear(element, num_bonds):
    """Check if an element with given bonds should be linear"""
    linear_elements = {
        'C': [2],  # sp hybridized carbon
        'N': [2],  # Linear nitrogen compounds
        'O': [],   # Not typically linear
        'S': [],
        'Be': [2], # BeF2, etc.
    }
    
    if element in linear_elements:
        return num_bonds in linear_elements[element]
    
    return num_bonds == 2 and element in ['Be', 'Hg', 'Zn']

def standardize_bond_lengths(editor):
    """Standardize all bond lengths based on atom radii"""
    for bond in editor.bonds:
        atom1 = editor.atoms[bond.atom1_id]
        atom2 = editor.atoms[bond.atom2_id]
        
        # Calculate ideal bond length
        radius1 = get_element_radius_2d(atom1.element)
        radius2 = get_element_radius_2d(atom2.element)
        ideal_length = (radius1 + radius2) * 2.0
        
        # Calculate current length
        dx = atom2.x - atom1.x
        dy = atom2.y - atom1.y
        current_length = math.sqrt(dx**2 + dy**2)
        
        if current_length > 0 and abs(current_length - ideal_length) > 5:
            # Adjust atom2 position
            scale = ideal_length / current_length
            new_x = atom1.x + dx * scale
            new_y = atom1.y + dy * scale
            
            # Only move if not too drastic
            move_distance = math.sqrt((new_x - atom2.x)**2 + (new_y - atom2.y)**2)
            if move_distance < ideal_length:
                atom2.x = new_x
                atom2.y = new_y

def get_connected_atoms_list(editor, atom_id):
    """Get list of connected atom IDs"""
    connected = []
    for bond in editor.bonds:
        if bond.atom1_id == atom_id:
            connected.append(bond.atom2_id)
        elif bond.atom2_id == atom_id:
            connected.append(bond.atom1_id)
    return connected

def redraw_all_elements(editor):
    """Redraw all atoms and bonds with updated positions"""
    # Update atom visuals
    for atom_id, atom in editor.atoms.items():
        # Update oval position
        radius = atom.radius
        editor.canvas_2d.coords(
            atom.canvas_id,
            atom.x - radius, atom.y - radius,
            atom.x + radius, atom.y + radius
        )
        
        # Update text position
        editor.canvas_2d.coords(atom.text_id, atom.x, atom.y)
    
    # Update bond visuals
    from canvas_operations import draw_bond, delete_bond
    for bond in editor.bonds:
        # Delete old bond visual
        if bond.canvas_id:
            if isinstance(bond.canvas_id, tuple):
                for cid in bond.canvas_id:
                    editor.canvas_2d.delete(cid)
            else:
                editor.canvas_2d.delete(bond.canvas_id)
        
        # Redraw bond
        atom1 = editor.atoms[bond.atom1_id]
        atom2 = editor.atoms[bond.atom2_id]
        canvas_id = draw_bond(editor, atom1, atom2, bond.bond_type)
        bond.canvas_id = canvas_id
        
        # Move bond behind atoms
        if canvas_id:
            if isinstance(canvas_id, tuple):
                for cid in canvas_id:
                    editor.canvas_2d.tag_lower(cid)
            else:
                editor.canvas_2d.tag_lower(canvas_id)
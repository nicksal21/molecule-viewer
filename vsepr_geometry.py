"""
VSEPR geometry calculations for 3D molecular structures
"""

import numpy as np
import math
from components import BondType

def calculate_molecular_geometry(editor, central_atom_id, connected_atoms):
    """Calculate and apply VSEPR geometry with proper bond lengths"""
    
    central_atom = editor.atoms[central_atom_id]
    num_atoms = len(connected_atoms)
    
    # Skip if too few atoms
    if num_atoms < 2:
        return False
    
    # Calculate lone pairs
    lone_pairs = estimate_lone_pairs(central_atom.element, num_atoms)
    steric_number = num_atoms + lone_pairs
    
    # Get the appropriate geometry positions
    positions = get_vsepr_positions(steric_number, lone_pairs)
    
    if positions is None or len(positions) < num_atoms:
        return False
    
    # Calculate actual bond lengths from 2D
    from element_data import get_element_radius_3d
    
    # Standard 3D bond length
    central_radius = get_element_radius_3d(central_atom.element)
    
    # Apply positions to connected atoms
    for i, connected_id in enumerate(connected_atoms):
        if i < len(positions) and connected_id in editor.atoms:
            connected_atom = editor.atoms[connected_id]
            pos = positions[i]
            
            # Calculate bond length based on atom sizes
            connected_radius = get_element_radius_3d(connected_atom.element)
            bond_length = (central_radius + connected_radius) * 1.8  # Reasonable 3D spacing
            
            # Set new 3D position
            connected_atom.x3d = central_atom.x3d + pos[0] * bond_length
            connected_atom.y3d = central_atom.y3d + pos[1] * bond_length
            connected_atom.z3d = central_atom.z3d + pos[2] * bond_length
            connected_atom.z3d_set = True  # Mark as explicitly set
    
    return True

def estimate_lone_pairs(element, num_bonds):
    """Estimate number of lone pairs based on element and number of bonds"""
    # Valence electrons for common elements
    valence_electrons = {
        'H': 1, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'S': 6, 'P': 5,
        'Cl': 7, 'Br': 7, 'I': 7, 'B': 3, 'Si': 4, 'Se': 6
    }
    
    if element not in valence_electrons:
        return 0
    
    val_e = valence_electrons[element]
    
    # Simple estimation: (valence_electrons - num_bonds) / 2
    remaining = val_e - num_bonds
    lone_pairs = max(0, remaining // 2)
    
    # Special cases
    if element == 'N' and num_bonds == 3:
        lone_pairs = 1  # Ammonia-like
    elif element == 'O' and num_bonds == 2:
        lone_pairs = 2  # Water-like
    elif element == 'S' and num_bonds == 4:
        lone_pairs = 1  # SF4-like
    elif element == 'S' and num_bonds == 6:
        lone_pairs = 0  # SF6
    
    return lone_pairs

def get_vsepr_positions(steric_number, lone_pairs):
    """Get 3D positions based on VSEPR theory"""
    
    if steric_number == 2 and lone_pairs == 0:
        # Linear (180°)
        return [
            np.array([1, 0, 0]),
            np.array([-1, 0, 0])
        ]
    
    elif steric_number == 3:
        if lone_pairs == 0:
            # Trigonal planar (120°)
            return [
                np.array([1, 0, 0]),
                np.array([-0.5, 0.866, 0]),
                np.array([-0.5, -0.866, 0])
            ]
        elif lone_pairs == 1:
            # Bent (120°)
            return [
                np.array([1, 0, 0]),
                np.array([-0.5, 0.866, 0])
            ]
    
    elif steric_number == 4:
        if lone_pairs == 0:
            # Tetrahedral (109.5°)
            return get_tetrahedral_positions()
        elif lone_pairs == 1:
            # Trigonal pyramidal
            positions = get_tetrahedral_positions()
            return positions[:3]  # Remove one position for lone pair
        elif lone_pairs == 2:
            # Bent (104.5°)
            angle = math.radians(104.5)
            return [
                np.array([math.cos(angle/2), math.sin(angle/2), 0]),
                np.array([math.cos(angle/2), -math.sin(angle/2), 0])
            ]
    
    elif steric_number == 5:
        if lone_pairs == 0:
            # Trigonal bipyramidal
            return get_trigonal_bipyramidal_positions()
        elif lone_pairs == 1:
            # Seesaw
            positions = get_trigonal_bipyramidal_positions()
            return positions[:4]  # Remove equatorial position
        elif lone_pairs == 2:
            # T-shaped
            positions = get_trigonal_bipyramidal_positions()
            return [positions[0], positions[3], positions[4]]  # Keep axial + 1 equatorial
        elif lone_pairs == 3:
            # Linear
            return [
                np.array([0, 0, 1]),
                np.array([0, 0, -1])
            ]
    
    elif steric_number == 6:
        if lone_pairs == 0:
            # Octahedral
            return get_octahedral_positions()
        elif lone_pairs == 1:
            # Square pyramidal
            positions = get_octahedral_positions()
            return positions[:5]
        elif lone_pairs == 2:
            # Square planar
            positions = get_octahedral_positions()
            return positions[:4]
    
    # Default fallback - distribute evenly on sphere
    return distribute_on_sphere(steric_number - lone_pairs)

def get_tetrahedral_positions():
    """Get tetrahedral positions (109.5° angles)"""
    # Tetrahedral vertices on unit sphere
    s = 1 / math.sqrt(3)
    return [
        np.array([s, s, s]),
        np.array([s, -s, -s]),
        np.array([-s, s, -s]),
        np.array([-s, -s, s])
    ]

def get_trigonal_bipyramidal_positions():
    """Get trigonal bipyramidal positions"""
    return [
        np.array([1, 0, 0]),      # Equatorial
        np.array([-0.5, 0.866, 0]),  # Equatorial
        np.array([-0.5, -0.866, 0]), # Equatorial
        np.array([0, 0, 1]),       # Axial
        np.array([0, 0, -1])       # Axial
    ]

def get_octahedral_positions():
    """Get octahedral positions (90° angles)"""
    return [
        np.array([1, 0, 0]),
        np.array([-1, 0, 0]),
        np.array([0, 1, 0]),
        np.array([0, -1, 0]),
        np.array([0, 0, 1]),
        np.array([0, 0, -1])
    ]

def distribute_on_sphere(n):
    """Distribute n points evenly on a unit sphere (fallback)"""
    points = []
    
    if n == 1:
        return [np.array([1, 0, 0])]
    
    # Use golden ratio spiral for even distribution
    golden_ratio = (1 + math.sqrt(5)) / 2
    
    for i in range(n):
        theta = 2 * math.pi * i / golden_ratio
        phi = math.acos(1 - 2 * (i + 0.5) / n)
        
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        
        points.append(np.array([x, y, z]))
    
    return points

def apply_rotation_to_match_2d(editor, central_atom_id, connected_atoms):
    """Rotate the 3D structure to best match the 2D projection"""
    central = editor.atoms[central_atom_id]
    
    if len(connected_atoms) < 2:
        return
    
    # Get first bond vector in 2D
    first_connected = editor.atoms[connected_atoms[0]]
    vec_2d = np.array([
        first_connected.x - central.x,
        first_connected.y - central.y
    ])
    vec_2d = vec_2d / np.linalg.norm(vec_2d)
    
    # Get first bond vector in 3D
    vec_3d = np.array([
        first_connected.x3d - central.x3d,
        first_connected.y3d - central.y3d,
        first_connected.z3d - central.z3d
    ])
    vec_3d = vec_3d / np.linalg.norm(vec_3d)
    
    # Calculate rotation to align 3D with 2D projection
    # This is simplified - a full implementation would use quaternions
    # For now, we'll keep the default orientation from VSEPR
    pass
"""
3D visualization module
"""

import numpy as np
from components import BondType, ATOM_RADIUS_3D
from element_data import get_element_color

def update_3d_view(editor):
    """Update the 3D visualization with proper shading"""
    editor.ax_3d.clear()
    editor.setup_3d_view()
    
    if not editor.atoms:
        editor.canvas_3d.draw()
        return
    
    # Calculate 3D positions using VSEPR theory
    calculate_3d_positions_vsepr(editor)
    
    # Set up lighting (from camera)
    setup_lighting(editor)
    
    # Draw atoms
    for atom_id, atom in editor.atoms.items():
        draw_atom_3d(editor, atom)
    
    # Draw bonds
    for bond in editor.bonds:
        draw_bond_3d(editor, bond)
    
    # Set cubic aspect ratio
    set_cubic_aspect(editor)
    
    editor.ax_3d.view_init(elev=20, azim=45)
    
    # Enable mouse interaction for 3D view
    setup_3d_interaction(editor)
    
    editor.canvas_3d.draw()

    
def setup_3d_interaction(editor):
    """Setup mouse interaction for 3D view"""
    if not hasattr(editor, '3d_interaction_setup'):
        editor.canvas_3d.mpl_connect('scroll_event', lambda event: on_3d_scroll(editor, event))
        editor.canvas_3d.mpl_connect('button_press_event', lambda event: on_3d_mouse_press(editor, event))
        editor.canvas_3d.mpl_connect('motion_notify_event', lambda event: on_3d_mouse_motion(editor, event))
        editor.canvas_3d.mpl_connect('button_release_event', lambda event: on_3d_mouse_release(editor, event))
        
        editor.rotating_3d = False
        editor.panning_3d = False
        editor.mouse_3d_start = None
        editor.view_3d_elev = 20
        editor.view_3d_azim = 45
        editor.view_3d_dist = 10
        setattr(editor, '3d_interaction_setup', True)

def calculate_3d_positions_vsepr(editor):
    """Calculate 3D positions using VSEPR theory with proper initialization"""
    # First, initialize all atoms with their 2D positions properly scaled
    for atom_id, atom in editor.atoms.items():
        atom.x3d = atom.x / 100
        atom.y3d = atom.y / 100
        atom.z3d = 0
    
    # Apply VSEPR only to molecules with 3+ atoms bonded to a center
    processed = set()
    
    for atom_id, atom in editor.atoms.items():
        if atom_id not in processed:
            connected = get_connected_atoms(editor, atom_id)
            
            # Only apply VSEPR if there are 3+ connections or special geometries
            if len(connected) >= 3 or should_apply_vsepr(editor, atom_id, connected):
                geometry_applied = calculate_molecular_geometry(editor, atom_id, connected)
                
                if geometry_applied:
                    processed.add(atom_id)
                    # Don't mark connected atoms as processed to allow chains
    
    # Handle special bond types (wedge and hash) that indicate 3D structure
    for bond in editor.bonds:
        if bond.bond_type == BondType.WEDGE:
            atom2 = editor.atoms[bond.atom2_id]
            if not hasattr(atom2, 'z3d_set') or not atom2.z3d_set:
                atom2.z3d = 1.0  # Come out of page
                atom2.z3d_set = True
        elif bond.bond_type == BondType.HASH:
            atom2 = editor.atoms[bond.atom2_id]
            if not hasattr(atom2, 'z3d_set') or not atom2.z3d_set:
                atom2.z3d = -1.0  # Go into page
                atom2.z3d_set = True

def draw_atom_3d(editor, atom):
    """Draw a 3D atom sphere with proper sizing (reduced size)"""
    from element_data import get_element_color, get_element_radius_3d
    
    color = get_element_color(atom.element)
    radius = get_element_radius_3d(atom.element) * 1.2  # Only 20% larger instead of 50%
    
    # Use stored 3D coordinates
    if not hasattr(atom, 'x3d'):
        atom.x3d = atom.x / 100
        atom.y3d = atom.y / 100
        atom.z3d = 0  # Default z to 0
    
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    x = radius * np.outer(np.cos(u), np.sin(v)) + atom.x3d
    y = radius * np.outer(np.sin(u), np.sin(v)) + atom.y3d
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + atom.z3d
    
    # Apply shading with ambient and diffuse lighting
    editor.ax_3d.plot_surface(
        x, y, z, color=color, alpha=1.0,
        shade=True,
        lightsource=editor.light_source,
        antialiased=True,
        edgecolor='none', 
        linewidth=0
    )
    
def on_3d_scroll(editor, event):
    """Handle scroll for 3D zoom"""
    if event.button == 'up':
        scale = 0.9
    elif event.button == 'down':
        scale = 1.1
    else:
        return
    
    # Adjust view limits for zoom
    xlim = editor.ax_3d.get_xlim()
    ylim = editor.ax_3d.get_ylim()
    zlim = editor.ax_3d.get_zlim()
    
    # Calculate new limits
    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2
    z_center = (zlim[0] + zlim[1]) / 2
    
    x_range = (xlim[1] - xlim[0]) * scale / 2
    y_range = (ylim[1] - ylim[0]) * scale / 2
    z_range = (zlim[1] - zlim[0]) * scale / 2
    
    editor.ax_3d.set_xlim([x_center - x_range, x_center + x_range])
    editor.ax_3d.set_ylim([y_center - y_range, y_center + y_range])
    editor.ax_3d.set_zlim([z_center - z_range, z_center + z_range])
    
    editor.canvas_3d.draw()

def on_3d_mouse_press(editor, event):
    """Handle mouse press for 3D view"""
    if event.button == 1:  # Left button - rotate
        editor.rotating_3d = True
        editor.mouse_3d_start = (event.x, event.y)
        editor.view_3d_elev = editor.ax_3d.elev
        editor.view_3d_azim = editor.ax_3d.azim
    elif event.button == 2:  # Middle button - pan
        editor.panning_3d = True
        editor.mouse_3d_start = (event.x, event.y)
        editor.xlim_start = editor.ax_3d.get_xlim()
        editor.ylim_start = editor.ax_3d.get_ylim()
        editor.zlim_start = editor.ax_3d.get_zlim()

def on_3d_mouse_motion(editor, event):
    """Handle mouse motion for 3D view"""
    if editor.rotating_3d and editor.mouse_3d_start and event.x and event.y:
        # Calculate rotation
        dx = event.x - editor.mouse_3d_start[0]
        dy = event.y - editor.mouse_3d_start[1]
        
        editor.ax_3d.view_init(
            elev=editor.view_3d_elev - dy,
            azim=editor.view_3d_azim - dx
        )
        editor.canvas_3d.draw()
        
    elif editor.panning_3d and editor.mouse_3d_start and event.x and event.y:
        # Calculate pan
        dx = (event.x - editor.mouse_3d_start[0]) * 0.01
        dy = (event.y - editor.mouse_3d_start[1]) * 0.01
        
        # Get current view range
        x_range = editor.xlim_start[1] - editor.xlim_start[0]
        y_range = editor.ylim_start[1] - editor.ylim_start[0]
        
        # Pan by adjusting limits
        editor.ax_3d.set_xlim([
            editor.xlim_start[0] - dx * x_range,
            editor.xlim_start[1] - dx * x_range
        ])
        editor.ax_3d.set_ylim([
            editor.ylim_start[0] + dy * y_range,
            editor.ylim_start[1] + dy * y_range
        ])
        
        editor.canvas_3d.draw()

def on_3d_mouse_release(editor, event):
    """Handle mouse release for 3D view"""
    editor.rotating_3d = False
    editor.panning_3d = False
    editor.mouse_3d_start = None

def draw_bond_3d(editor, bond):
    """Draw a 3D bond with proper orientations for double/triple bonds"""
    from element_data import get_element_color, get_element_radius_3d
    
    atom1 = editor.atoms[bond.atom1_id]
    atom2 = editor.atoms[bond.atom2_id]
    
    # Ensure atoms have 3D coordinates
    if not hasattr(atom1, 'x3d'):
        atom1.x3d = atom1.x / 100
        atom1.y3d = atom1.y / 100
        atom1.z3d = 0
    if not hasattr(atom2, 'x3d'):
        atom2.x3d = atom2.x / 100
        atom2.y3d = atom2.y / 100
        atom2.z3d = 0
    
    p1 = np.array([atom1.x3d, atom1.y3d, atom1.z3d])
    p2 = np.array([atom2.x3d, atom2.y3d, atom2.z3d])
    
    color1 = get_element_color(atom1.element)
    color2 = get_element_color(atom2.element)
    
    # Smaller radii for atoms (20% increase)
    radius1 = get_element_radius_3d(atom1.element) * 1.2
    radius2 = get_element_radius_3d(atom2.element) * 1.2
    
    direction = p2 - p1
    length = np.linalg.norm(direction)
    
    if length > 0:
        unit_dir = direction / length
        p1_adjusted = p1 + unit_dir * radius1 * 0.9
        p2_adjusted = p2 - unit_dir * radius2 * 0.9
        
        if bond.bond_type == BondType.SINGLE:
            draw_bicolor_cylinder(editor, p1_adjusted, p2_adjusted, color1, color2, 0.08)
        
        elif bond.bond_type == BondType.DOUBLE:
            # Use 2D bond orientation to determine offset direction
            offset_dir = get_bond_offset_direction(atom1, atom2)
            offset = offset_dir * 0.10
            draw_bicolor_cylinder(editor, p1_adjusted + offset, p2_adjusted + offset, color1, color2, 0.06)
            draw_bicolor_cylinder(editor, p1_adjusted - offset, p2_adjusted - offset, color1, color2, 0.06)
        
        elif bond.bond_type == BondType.TRIPLE:
            # Use 2D bond orientation for offset
            offset_dir = get_bond_offset_direction(atom1, atom2)
            offset = offset_dir * 0.12
            draw_bicolor_cylinder(editor, p1_adjusted, p2_adjusted, color1, color2, 0.05)
            draw_bicolor_cylinder(editor, p1_adjusted + offset, p2_adjusted + offset, color1, color2, 0.05)
            draw_bicolor_cylinder(editor, p1_adjusted - offset, p2_adjusted - offset, color1, color2, 0.05)
        
        elif bond.bond_type == BondType.WEDGE:
            draw_bicolor_cylinder(editor, p1_adjusted, p2_adjusted, color1, color2, 0.12)
        
        elif bond.bond_type == BondType.HASH:
            segments = 5
            for i in range(segments):
                if i % 2 == 0:
                    t1 = i / segments
                    t2 = (i + 0.5) / segments
                    seg_p1 = p1_adjusted + (p2_adjusted - p1_adjusted) * t1
                    seg_p2 = p1_adjusted + (p2_adjusted - p1_adjusted) * t2
                    color = color1 if i < segments/2 else color2
                    draw_cylinder_segment(editor, seg_p1, seg_p2, 0.06, color)

def draw_bicolor_cylinder(editor, p1, p2, color1, color2, radius):
    """Draw cylinder with two colors"""
    midpoint = (p1 + p2) / 2
    draw_cylinder_segment(editor, p1, midpoint, radius, color1)
    draw_cylinder_segment(editor, midpoint, p2, radius, color2)

def draw_cylinder_segment(editor, p1, p2, radius, color):
    """Draw a cylinder segment with shading"""
    v = p2 - p1
    height = np.linalg.norm(v)
    if height == 0:
        return
    
    v = v / height
    
    not_v = np.array([1, 0, 0])
    if np.allclose(v, not_v):
        not_v = np.array([0, 1, 0])
    
    n1 = np.cross(v, not_v)
    n1 = n1 / np.linalg.norm(n1)
    n2 = np.cross(v, n1)
    
    theta = np.linspace(0, 2*np.pi, 30)  # More segments for smoother cylinders
    z = np.linspace(0, height, 20)
    theta_grid, z_grid = np.meshgrid(theta, z)
    
    x_cyl = radius * np.cos(theta_grid)
    y_cyl = radius * np.sin(theta_grid)
    
    points = np.zeros((20, 30, 3))
    for i in range(20):
        for j in range(30):
            point = p1 + z_grid[i, j] * v + x_cyl[i, j] * n1 + y_cyl[i, j] * n2
            points[i, j] = point
    
    editor.ax_3d.plot_surface(
        points[:,:,0], points[:,:,1], points[:,:,2],
        color=color, alpha=1.0, 
        shade=True,  # Enable shading for cylinders
        lightsource=editor.light_source,
        antialiased=True,
        edgecolor='none', 
        linewidth=0
    )
    
def get_camera_light(editor):
    """Create a light source from camera position"""
    from matplotlib.colors import LightSource
    
    # Get camera position (approximation based on view angles)
    elev = editor.ax_3d.elev if hasattr(editor.ax_3d, 'elev') else 20
    azim = editor.ax_3d.azim if hasattr(editor.ax_3d, 'azim') else 45
    
    # Create light source from camera direction
    # Invert angles to point from camera to origin
    light = LightSource(azdeg=azim, altdeg=elev, hsv_min_val=0.3, hsv_max_val=0.9)
    return light

def draw_bicolor_cylinder_shaded(editor, p1, p2, color1, color2, radius):
    """Draw cylinder with two colors and shading"""
    midpoint = (p1 + p2) / 2
    draw_cylinder_segment_shaded(editor, p1, midpoint, radius, color1)
    draw_cylinder_segment_shaded(editor, midpoint, p2, radius, color2)
    
def set_cubic_aspect(editor):
    """Set cubic aspect ratio for 3D plot"""
    # Get current limits
    xlim = editor.ax_3d.get_xlim()
    ylim = editor.ax_3d.get_ylim()
    zlim = editor.ax_3d.get_zlim()
    
    # Calculate ranges
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    z_range = zlim[1] - zlim[0]
    
    # Find maximum range
    max_range = max(x_range, y_range, z_range)
    
    # Calculate centers
    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2
    z_center = (zlim[0] + zlim[1]) / 2
    
    # Set equal ranges
    half_range = max_range / 2
    editor.ax_3d.set_xlim([x_center - half_range, x_center + half_range])
    editor.ax_3d.set_ylim([y_center - half_range, y_center + half_range])
    editor.ax_3d.set_zlim([z_center - half_range, z_center + half_range])
    
    # Set box aspect ratio to be equal
    editor.ax_3d.set_box_aspect([1, 1, 1])
    
def setup_lighting(editor):
    """Setup lighting from camera position"""
    from matplotlib.colors import LightSource
    
    # Get current view angles
    elev = editor.ax_3d.elev if hasattr(editor.ax_3d, 'elev') else 20
    azim = editor.ax_3d.azim if hasattr(editor.ax_3d, 'azim') else 45
    
    # Create light source from camera direction
    # Ambient + diffuse only (no specular)
    editor.light_source = LightSource(azdeg=azim, altdeg=elev)
    
def get_bond_offset_direction(atom1, atom2):
    """Calculate offset direction for double/triple bonds based on 2D positions"""
    # Get 2D bond vector
    dx = atom2.x - atom1.x
    dy = atom2.y - atom1.y
    length_2d = np.sqrt(dx**2 + dy**2)
    
    if length_2d == 0:
        return np.array([0, 0, 1])
    
    # Perpendicular in 2D plane (rotate 90 degrees)
    perp_x = -dy / length_2d
    perp_y = dx / length_2d
    
    # Convert to 3D (keep in XY plane)
    return np.array([perp_x / 100, perp_y / 100, 0])

def should_apply_vsepr(editor, atom_id, connected_atoms):
    """Determine if VSEPR should be applied to this atom"""
    if len(connected_atoms) < 2:
        return False
    
    atom = editor.atoms[atom_id]
    
    # Apply VSEPR for atoms that typically have 3D geometry
    vsepr_elements = {'C', 'N', 'O', 'S', 'P', 'Si', 'B'}
    
    # Check if central atom is a typical VSEPR center
    if atom.element in vsepr_elements:
        # Check for sp3 carbons (4 bonds or 3 bonds + implicit H)
        if atom.element == 'C' and len(connected_atoms) >= 3:
            return True
        # Nitrogen with 3+ bonds (pyramidal)
        elif atom.element == 'N' and len(connected_atoms) >= 2:
            return True
        # Oxygen with 2 bonds (bent)
        elif atom.element == 'O' and len(connected_atoms) == 2:
            return True
        # Sulfur and Phosphorus centers
        elif atom.element in {'S', 'P'} and len(connected_atoms) >= 2:
            return True
    
    return False

def get_perpendicular_vector(vector):
    """Get a perpendicular vector for bond offset"""
    # Find a vector perpendicular to the input
    if abs(vector[2]) < 0.9:
        perp = np.cross(vector, [0, 0, 1])
    else:
        perp = np.cross(vector, [1, 0, 0])
    
    return perp / np.linalg.norm(perp)

def get_connected_atoms(editor, central_atom_id):
    """Get list of atoms directly bonded to the central atom"""
    connected = []
    for bond in editor.bonds:
        if bond.atom1_id == central_atom_id:
            connected.append(bond.atom2_id)
        elif bond.atom2_id == central_atom_id:
            connected.append(bond.atom1_id)
    return connected
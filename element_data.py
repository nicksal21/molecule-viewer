"""
Element data, colors, and periodic table information
"""

import colorsys
import periodictable as pt

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

def get_element_info(element_symbol):
    """Get element information from periodic table"""
    try:
        element = getattr(pt, element_symbol)
        return {
            'name': element.name,
            'number': element.number,
            'mass': element.mass,
            'symbol': element_symbol
        }
    except:
        return {
            'name': element_symbol,
            'number': 0,
            'mass': 0,
            'symbol': element_symbol
        }

def should_use_white_text(element_symbol, color=None):
    """Determine if white text should be used on element background"""
    if element_symbol in ['C', 'N', 'Br', 'I']:
        return True
    if color and len(color) == 7 and color[1:3] < '60':
        return True
    return False

def get_element_radius_2d(element_symbol):
    """Get 2D radius for element based on periodic table row"""
    try:
        element = getattr(pt, element_symbol)
        num = element.number
        
        # Determine row (period) in periodic table
        if num <= 2:  # H, He
            row = 1
        elif num <= 10:  # Li to Ne
            row = 2
        elif num <= 18:  # Na to Ar
            row = 3
        elif num <= 36:  # K to Kr
            row = 4
        elif num <= 54:  # Rb to Xe
            row = 5
        elif num <= 86:  # Cs to Rn (includes lanthanides)
            row = 6
        else:  # Fr onwards (includes actinides)
            row = 7
        
        # Calculate radius: 0.7 + (row-1) * 0.05
        radius_scale = 0.7 + (row - 1) * 0.05
        return 20 * radius_scale  # Base radius of 20 pixels (reduced for better spacing)
        
    except:
        return 20  # Default radius

def get_element_radius_3d(element_symbol):
    """Get 3D radius for element based on periodic table row"""
    try:
        element = getattr(pt, element_symbol)
        num = element.number
        
        # Determine row (period) in periodic table
        if num <= 2:  # H, He
            row = 1
        elif num <= 10:  # Li to Ne
            row = 2
        elif num <= 18:  # Na to Ar
            row = 3
        elif num <= 36:  # K to Kr
            row = 4
        elif num <= 54:  # Rb to Xe
            row = 5
        elif num <= 86:  # Cs to Rn (includes lanthanides)
            row = 6
        else:  # Fr onwards (includes actinides)
            row = 7
        
        # Calculate radius: 0.7 + (row-1) * 0.05
        radius_scale = 0.7 + (row - 1) * 0.05
        return 0.3 * radius_scale  # Base radius of 0.3 units (smaller for better proportions)
        
    except:
        return 0.3  # Default radius

# Periodic table layout for dialog
PERIODIC_TABLE_LAYOUT = [
    ['H', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'He'],
    ['Li', 'Be', '', '', '', '', '', '', '', '', '', '', 'B', 'C', 'N', 'O', 'F', 'Ne'],
    ['Na', 'Mg', '', '', '', '', '', '', '', '', '', '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],
    ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],
    ['Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],
    ['Cs', 'Ba', '*', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'],
    ['Fr', 'Ra', '**', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'],
]

LANTHANIDES = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
ACTINIDES = ['Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr']
COMMON_ELEMENTS = ['H', 'C', 'N', 'O', 'F', 'P', 'S', 'Cl', 'Br', 'I']
"""
Core components: data structures, enums, and basic classes
"""

from dataclasses import dataclass
from enum import Enum

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
    radius: float = 25
    x3d: float = 0.0
    y3d: float = 0.0
    z3d: float = 0.0
    
@dataclass
class Bond:
    atom1_id: int
    atom2_id: int
    bond_type: BondType
    canvas_id: int = None

# Canvas and 3D settings
ATOM_RADIUS_2D = 25
BOND_LENGTH_2D = 80
ATOM_RADIUS_3D = 0.5
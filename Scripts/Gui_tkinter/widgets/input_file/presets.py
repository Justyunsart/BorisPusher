
from enum import Enum

class BRingPresets(Enum):
    """presets for magnetic configurations"""
    # shape, offset, charge, diameter
    hex_100k = ['hexahedron', '1.1', '100000', '0.75']

class ERingPresets(Enum):
    """presets for electric ring configurations"""
    # shape, offset, charge, diameter
    hex_100k = ['hexahedron', '1.1', '1e-11', '0.75']


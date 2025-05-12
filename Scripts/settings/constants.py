from dataclasses import dataclass
"""
A place to hold physics constants.
"""

# PARTICLE/ION INFORMATION 
"""
Base class for ion information.
"""
@dataclass
class ion():
    name : str
    mass : float # KG
    q : float # COULOMBS
    anum : float # atomic number

proton = ion(name="proton", mass=1.672e-27, q=1.602e-19, anum=1)

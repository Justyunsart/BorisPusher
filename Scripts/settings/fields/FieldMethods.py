'''
Intended to be an easy way to keep track of all the different methods used to calculate B and E fields.
'''
from enum import (Enum, auto)
from settings.fields.FieldMethods_Impl import *

from RETerry.bob_e import bob_e_from_collection
from EFieldFJW.ys_3d_disk import compute_disk_with_collection

"""
Below: deprecated. Kept so that deprecated scripts that use the values below don't raise a stink
"""
class E_Methods(Enum):
    Zero = Zero_impl
    Fw = Fw_impl
    Bob_e = bob_e_impl
    Fwyr_e = Fwyr_e

class E_Methods1(Enum):
    zero = Zero_impl
    bob_e = bob_e_impl
    fw_e = Fwyr_e
    disk_e = None # implementation is elsewhere, as the new architecture doesn't need these classes

class E_Methods2(Enum):
    """
    This one has the name as the key, and its callable func. as the value.
    The callable has certain requirements:
        1. It needs to be able to take in a predefined shape (update this)
        2. These are in Cartesian coords
    """
    bob_e = bob_e_from_collection
    disk_e = compute_disk_with_collection #reminder that this only expects 1 coord at a time, and needs an executor.
    washer_potential = None



class B_Methods(Enum):
    Zero = Zero_impl
    Magpy = 1 # calculated using magpylib's analytic equation

class FieldGraph_Methods(Enum):
    """
    Options for field graph views you can choose in the GUI.
    """
    E = 0
    B = 1
    E_B_lineout = 2
    E_Streamline = 3
    E_lineout = 4
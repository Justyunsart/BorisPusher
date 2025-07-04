'''
Intended to be an easy way to keep track of all the different methods used to calculate B and E fields.
'''
from enum import (Enum, auto)
from settings.fields.FieldMethods_Impl import (Fw_impl, Zero_impl, bob_e_impl, Fwyr_e
)

class E_Methods(Enum):
    Zero = Zero_impl
    Fw = Fw_impl
    Bob_e = bob_e_impl
    Fwyr_e = Fwyr_e

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
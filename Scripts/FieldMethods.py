'''
Intended to be an easy way to keep track of all the different methods used to calculate B and E fields.
'''
from enum import (Enum, auto)
from FieldMethods_Impl import (Fw_impl, Zero_impl, bob_e_impl)

class E_Methods(Enum):
    Zero = Zero_impl
    Fw = Fw_impl
    Bob_e = bob_e_impl

class B_Methods(Enum):
    Zero = Zero_impl
    Magpy = auto() # calculated using magpylib's analytic equation
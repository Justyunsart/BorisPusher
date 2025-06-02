
"""
Internal TempManager reference names.
Stored here for consistency and ease of use.
"""

# TEMP MANAGER NAMES
manager_1 = "m_params" # files die after calculate button is pressed.

# TEMP FILE NAMES
m1f1 = "params"
m1f2 = "traj_1"

################################################################################
# Below are definitions for field names inside m1f1
from enum import Enum
class param_keys(Enum):
    coil_file = "Location of the magnetic coil configuration input file"
    mag_coil = "Binary of the magpylib.Collection object of the selected coil input"
    coil_name = "Name of the coil input file"

    bob_e_file = "Location of the input file representing the circle charges used for the bob_e e-field method"
    bob_e_coil = "The magpylib.Collection binary container for the bob_e method. This is used purely for graphs, the built-in magpy funcs don't apply"
    bob_e_name = "Name of the bob_e input file"

    particle_file = "Location of the magnetic particle configuration input file"
    particle_name = "Name of the particle input file"

    dt = "Default timestep value (seconds)"
    dt_bob = "boolean value for whether the simulation should run with bob's variable timestep"
    numsteps = "Number of time steps to simulate"

    field_methods = "Nested dictionary of b, e field methods and associated parameters"
    b = "the b-field parameters inside the field_methods dictionary"
    e = "the e-field parameters inside the field_methods dictionary"
    method = "the name of the field method used"
    params = "the parameters that are involved with the given field method"

    output_location = "runtime-configured location for the output file"
    output_name = "runtime-configured name for the output file"
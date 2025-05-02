import os
"""
Root level script that holds info for internal scripts.
This only holds unchanging and baseline information that cannot be defined elsewhere.

For settings involving project parameters, look in ().../BorisPusher/Scripts/settings/).
"""
# DIRECTORIES
DIR_ROOT = os.path.dirname(os.path.abspath(__file__)) # project root (BorisPusher/)

# FILE/FOLDER NAMES
NAME_INPUTS = "Inputs"
NAME_COILS = "Coils"
NAME_PARTICLES = "Particles"
NAME_BOB_E_CHARGES = "Bobs"

# FOLDER STRUCTS
## key = subdir, value = list of subsubdir(s)
_input_preset = "Presets" # name of the presets folder, if present.
FOLDER_INPUTS = { # subdirs of the inputs folder
    NAME_COILS:[_input_preset], 
    NAME_PARTICLES:[_input_preset], 
    NAME_BOB_E_CHARGES:[_input_preset]}
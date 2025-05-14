import os
import sys
"""
Root level script that holds info for internal scripts.
This only holds unchanging and baseline information that cannot be defined elsewhere.

For settings involving project parameters, look in ().../BorisPusher/Scripts/settings/).
"""
# SYSTEM INFO
PLATFORM = sys.platform # win32, linux, or darwin

# FILE/FOLDER NAMES
NAME_INPUTS = "Inputs"
NAME_COILS = "CoilConfigurations"
NAME_PARTICLES = "ParticleConditions"
NAME_BOB_E_CHARGES = "Bobs"
NAME_lastUsed = "lastUsed" # a text file holding the last used configs.

NAME_OUTPUTS = "Outputs"

# DIRECTORIES
DIR_ROOT = os.path.dirname(os.path.abspath(__file__)) # project root (BorisPusher/)
DIR_INPUTS = os.path.join(DIR_ROOT, NAME_INPUTS)
DIR_INPUTS_COILS = os.path.join(DIR_INPUTS, NAME_COILS)
DIR_INPUTS_PARTICLES = os.path.join(DIR_INPUTS, NAME_PARTICLES)


# FOLDER STRUCTS
## key = subdir, value = list of subsubdir(s)
_input_preset = "Presets" # name of the presets folder, if present.
FOLDER_INPUTS = { # subdirs of the inputs folder
    NAME_COILS:[_input_preset], 
    NAME_PARTICLES:[_input_preset], 
    NAME_BOB_E_CHARGES:[_input_preset]}
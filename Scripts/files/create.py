import os
from definitions import FOLDER_INPUTS, NAME_INPUTS, DIR_ROOT
from files.funcs import check_subdirs
import configparser
from settings.configs.funcs.config_reader import runtime_configs
from xattr import getxattr
from settings.defaults.coils import coil_cust_attr_name

"""
Helper functions involving the creation of known directories (like the inputs folder).
Right now it's only limited to the Inputs folder, but it totally could expand maybe if need be.
"""
def create_inputs_subdirs(inputs_path):
    """
    helper function for creating the inputs folder's subdirs

    # PARAMETERS
    inputs_path(str): inputs dir
    """
    check_subdirs(inputs_path, list(FOLDER_INPUTS.keys()), FOLDER_INPUTS)

def create_inputs_folder():
    """
    Runs in case the program does not detect an inputs folder in the project root.
    Creates a new inputs folder for the user.
    """
    if not os.path.exists(runtime_configs['Paths']['inputs']):
        os.mkdir(runtime_configs['Paths']['inputs'])

    # create subfolders
    create_inputs_subdirs(runtime_configs['Paths']['inputs'])
    
    return True

def create_ini_from_dict(save_path=DIR_ROOT, ini_name='new_ini.ini', dct:dict=None):
    assert dct is not None, print(f"PASS A DICTIONARY TO: Scripts.files.create.create_ini_from_dict()")
    config = configparser.ConfigParser()

        # iterate over the dict while adding to the config parser obj
    for sec, item in dct.items():
        config.add_section(sec)
        if type(item) == dict:
            for k, v in item.items():
                config.set(sec, k, v)
        
        # save output ini to file
    with open(os.path.join(save_path, ini_name), 'w') as f:
        config.write(f)

#########################################################################################################
# HELPERS FOR CREATING OUTPUT FOLDER SUBDIRS

"""
Helper function for reading the custom attribute for the input file I made to keep track of the used
preset.

Returns the preset value if read, and "NULL" if any errors happen.
"""
def get_coil_preset_attr_val(path):
    try:
        return getxattr(path, coil_cust_attr_name).decode()
    except OSError:
        return "Custom"

"""
Returns the unique mags of the configuration's amps.
"""
from magpylib import Collection
def get_unique_coil_collection_amps(c:Collection):
    out:set = set()
    for coil in c.children:
        out.add(abs(coil.current))
    return ", ".join(map(str, out))

"""
runs BEFORE any calculations happen.
Creates (if needed) the subdirs where all output diagnostics and checkpoint stuff will be stored
"""
def create_output_subdirs(output_root_path, c, coil_file_path):
        # Gather the subdir names first
    preset_name = get_coil_preset_attr_val(coil_file_path)
    amp_name = get_unique_coil_collection_amps(c)
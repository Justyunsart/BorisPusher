import os
from definitions import FOLDER_INPUTS, NAME_INPUTS, DIR_ROOT, PLATFORM
from files.funcs import check_subdirs
import configparser
from settings.configs.funcs.config_reader import runtime_configs
if PLATFORM != 'win32':
    from xattr import getxattr
from settings.defaults.coils import coil_cust_attr_name

from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import manager_1, m1f1

from files.hdf5.output_file_structure import create_h5_output_file

from settings.configs.funcs.config_reader import runtime_configs

default_output_file_name = ""
default_output_file_dir = ""

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
        if PLATFORM != 'win32':
            return getxattr(path, coil_cust_attr_name).decode()
        else:
            with open(f"{path}:{coil_cust_attr_name}", "r") as f:
                return f.read()
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
returns a string formatted with 
numsteps_dt. This is considered the default name for the file.
"""
def get_output_name(path):
    global default_output_file_name
    d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
    default_output_file_name =  f"ns-{d['numsteps']}_dt-{d['dt']}"
    i = 1
    while os.path.exists(os.path.join(path, default_output_file_name)):
        default_output_file_name = f"ns-{d['numsteps']}_dt-{d['dt']}_{i}"
        i += 1
    return default_output_file_name

"""
populates global var with the default location of the output subdir, based on the runtimeconfigs.
"""
def get_default_output_dir():
    global default_output_file_dir
        # subdir structure based on parameters
    d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
    preset = get_coil_preset_attr_val(d['particle_file'])
    current = get_unique_coil_collection_amps(d['mag_coil'])
    b = d['field_methods']['b']['method']
    e = d['field_methods']['e']['method']
    _p = os.path.join(preset, current, b, e)

        # also need to get the runtimeconfig for the default output location
    def_out = runtime_configs['Paths']['output']
    default_output_file_dir = os.path.join(str(def_out), str(_p))


"""
returns a path of the placement for the output file based on params
in the order of:

preset/current/b/e
"""
def get_output_subdir():
    d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
    preset = get_coil_preset_attr_val(d['particle_file'])
    current = get_unique_coil_collection_amps(d['mag_coil'])
    b = d['field_methods']['b']['method']
    e = d['field_methods']['e']['method']
    name = get_output_name(os.path.join(preset, current, b, e))

    d["output_path"] = os.path.join(preset, current, b, e, name)
    d["hdf5_path"] = os.path.join(d["output_path"], 'data.hdf5')
    write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

    length = (d['numsteps'] * len(d["Particle_Df"])) + 1

    os.makedirs(os.path.join(str(runtime_configs['Paths']['outputs']), d['output_path']), exist_ok=True)
    create_h5_output_file(os.path.join(str(runtime_configs['Paths']['outputs']), d["hdf5_path"]), length)

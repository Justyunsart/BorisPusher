import os
from definitions import DIR_ROOT, NAME_INPUTS, FOLDER_INPUTS, NAME_OUTPUTS
from files.create import create_inputs_folder
from files.funcs import check_subdirs
from settings.configs.funcs.configs import create_default_config

"""
Functions for checking the validity of file stuff.
Expect these kinds of checks to run on application startup.
"""

"""
create the default .ini folder if it does not exist.
"""
def ini_checks():
    if not os.path.exists(os.path.join(DIR_ROOT, 'config.ini')):
        create_default_config()

def folder_checks():
    """
    Location of all types of folder checking. Call this to check all necessary folders.
    """
    input_folder_check()
    output_folder_check()

def input_folder_check():
    from settings.configs.funcs.config_reader import runtime_configs
    """
    Verifies that the program's root directory contains a valid Inputs folder.
    """
    try:
            # make the inputs folder if it doesnt exist at the default configured path.
        os.makedirs(runtime_configs['Paths']['inputs'], exist_ok=True)
            # Check that the root has an inputs folder in the first place:
        if(NAME_INPUTS not in os.listdir(runtime_configs['Paths']['inputs'])): # The folder with the specified name for input files does not exist.
            create_inputs_folder() # make sure the folder now exists with the right subdirs
            return True

        # Next, ensure that all directed subdirs are in the dir.
        check_subdirs(runtime_configs['Paths']['inputs'], list(FOLDER_INPUTS.keys()))

        return True
    except KeyError:
        print("KeyError for some reason")


"""
checks the runtime config's supposed location for the output dir.
creates it if it does not exist.

This just creates an empty dir: Its subdirs will be created during runtime if needed.
"""
def output_folder_check():
    from settings.configs.funcs.config_reader import runtime_configs
    if(not os.path.exists(runtime_configs['Paths']['Outputs'])):
        os.mkdir(runtime_configs['Paths']['Outputs'])



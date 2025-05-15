import os
from definitions import DIR_ROOT, NAME_INPUTS, FOLDER_INPUTS
from files.create import create_inputs_folder
from files.funcs import check_subdirs
from settings.configs import create_config
"""
Functions for checking the validity of file stuff.
Expect these kinds of checks to run on application startup.
"""

"""
create the default .ini folder if it does not exist.
"""
def ini_checks():
    if not os.path.exists(os.path.join(DIR_ROOT, 'config.ini')):
        create_config()

def folder_checks():
    """
    Location of all types of folder checking. Call this to check all necessary folders.
    """
    input_folder_check()

def input_folder_check():
    """
    Verifies that the program's root directory contains a valid Inputs folder.
    """
    # Check that the root has an inputs folder in the first place:
    if(NAME_INPUTS not in os.listdir(DIR_ROOT)): # The folder with the specified name for input files does not exist.
        create_inputs_folder() # make sure the folder now exists with the right subdirs
        return True
    
    # Next, ensure that all directed subdirs are in the dir.
    check_subdirs(os.path.join(DIR_ROOT, NAME_INPUTS), list(FOLDER_INPUTS.keys()))
    
    return True

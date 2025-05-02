import os
from definitions import FOLDER_INPUTS, NAME_INPUTS, DIR_ROOT
from funcs import check_subdirs

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
    inputs_path = os.path.join(DIR_ROOT, NAME_INPUTS) # full path to the new inputs folder

    # create the folder
    os.mkdir(inputs_path)

    # create subfolders
    create_inputs_subdirs(inputs_path)
    
    return True
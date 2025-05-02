import os
import pathlib

"""
Helper funcs for file handling
"""

def check_subdirs(base:str, names:list, dct=None):
    """
    Creates subdirectories based on the provided inputs.

    # PARAMETERS:
    base(str): the dir to create the subdirs to
    names(list/iterable): the subdir names
    dct(dict): A dictionary with keys = names, values = list of subsubdirs
    """
    for name in names:
        subdir_path = os.path.join(base, name)
        pathlib.Path.mkdir(pathlib.Path(subdir_path), exist_ok=True)
        
        if dct is not None:
            check_subdirs(os.path.join(base, name), dct[name])
    
    return True
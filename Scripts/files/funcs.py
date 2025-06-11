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

"""
It would be good to get a list of h5 files in the output directory that is sorted
by datetime of creation in descending order. 

Checks all files and subdirs walking from the input dir based on the inputted file extension
"""
def sorted_files_by_datetime(dir, extension='.h5', order='descending'):
    for subdir in pathlib.Path(rf'{dir}').glob('*/'):
        print(subdir)
        for f in sorted(subdir.rglob(f'*.{extension}'), key=os.path.getctime)[:-1]:
            print(f)

if __name__ == '__main__':
    outpath = os.path.normpath(os.path.join("D:\FromCDocuments\Boris_Usr", "Outputs"))
    sorted_files_by_datetime(outpath)
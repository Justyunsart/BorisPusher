import h5py
import numpy as np
from settings.configs.funcs.config_reader import runtime_configs
from pathlib import Path
import os
import pandas as pd
from Gui_tkinter.funcs.GuiEntryHelpers import File_to_Collection

def get_diag_values(row) -> dict:
    """
    Given an input of a single row (of an expected length, value order),
    output values to be used in the 'diags' dataset.

    the row input represents the first row  of the csv's conversion into a
    pandas dataframe.

    offset = maximum of the first three columns
    current = the 4th column
    diameter = the 5th column

    returns a dict with key/value pairs representing the name of the column
    and their respective value
    """
    offset = np.max(np.abs(np.array((float(row.iloc[0]), float(row.iloc[1]), float(row.iloc[2])),
                             dtype=np.float64)))
    current = float(row.iloc[3])
    diameter = float(row.iloc[4])

    return {
        'offset': offset,
        'current': current,
        'diameter': diameter,
    }

"""
Creates and saves a .h5 file storing a uniform coarse grid with a selected configuration's field.
"""
def check_if_overwrite(desired_file, input_file_path, diags_present)->bool:
    """
    If the selected option's .h5 file already exists (and has different input parameters), return True.
    Otherwise, return False.

    :params:
    desired_file(Path): a Path object that contains the dir to the desired file
    input_file_path(Path): a Path object that contains the dir to the input file
                           The first line is read to compare w/ the diags in the h5 file, if exists
    """
    # 1st check if an .h5 file with the same name already exists
    if not os.path.exists(desired_file): # if the path does not exist, then u always create one
        return True
    else:
        # GET H5 DIAGNOSTICS
        with h5py.File(desired_file, 'r') as f:
            diags_ds = f['src']['diags']
            diags_past = {
                'offset': diags_ds['offset'],
                'current': diags_ds['current'],
                'diameter': diags_ds['diameter']
            }

        # if the past and present dicts are the same, then you don't need to update the file.
        # however, if they are not the same, then you do want to overwrite.

        #print(f"check_if overwrite: past: {diags_past} present: {diags_present}")
        #print(f"returning {diags_past == diags_present}")
        return False if diags_past == diags_present else True

# numpy dtypes, so the h5 file can have named columns
dtype_diags = np.dtype([('diameter', np.float64),
                        ('current', np.float64),
                        ('offset', np.float64)])
'''
dtype_grid_data = np.dtype([('px', np.float64),
                            ('py', np.float64),
                            ('pz', np.float64),
                            ('fx', np.float64),
                            ('fy', np.float64),
                            ('fz', np.float64)])
'''

def check_grid_dir(path:Path)-> Path:
    """
    Assures that the parent dir of the input file has a 'grid' folder.
    returns the grid folder's path
    """
    # assemble the path to the grid dir
    parent_dir = path.parent
    grid_dir = parent_dir / 'grid'

    # create the dir if it exists
    os.makedirs(grid_dir, exist_ok=True)
    return grid_dir

def create_grid_h5(file_name, res, **kwargs):
    """
    Creates an empty .h5 file with the given structure.
    Expected to be populated during initial calculations.

    the dataset 'diags' will hold parameter information that lets the program
    know whether to overwrite the currently existing .h5 file nor not (if it exists)

    the dataset 'data' will hold all relevant grid/field information.
    """
    # Create file
    with h5py.File(file_name, 'w', libver='latest') as f:
        f.swmr_mode = True # single writer, multiple readers

        grp = f.create_group('/src')
        diags = f.create_dataset('/src/diags', (1,), dtype=dtype_diags)
        coords = f.create_dataset('/src/coords', (3, res, res, res), chunks=True,
                                dtype=np.float64)
        data = f.create_dataset('src/data', (3, res, res, res), chunks=True,
                                dtype=np.float64)

def precalculate_3d_grid(method, input_file_path, res=250, **kwargs):
    """
    :params:
    method(callable): the actual logic used to populate the field.
                      Takes a cartesian input, and poops out a cartesian output.
    input_file_name(str): the path to the input file. Used to create input corresponding grid files

    The coarse grid will, for now, be defined by a meshgrid composed of each axis being divided up into a linspace
    with 100 subdivisions.

    NOTE:
        Because methods may differ in their usage of the meshgrid, it is recommended that any deviations
        from the grid used in this function is accounted for in the inputted method
        (make sure the method u plug in here expects the grid format this function creates)
    """

    # MAKE SURE THE PLAYING FIELD IS KOSHER
    grid_dir = check_grid_dir(input_file_path) # does the grid_dir even exist?
    desired_path = grid_dir / f'{input_file_path.name}.hdf5' # .../grid/file.h5

    # read csv as a pd dataframe
    df = pd.read_csv(input_file_path) # THIS IS THE CURRENT CONFIGURATION'S DF REMEMBER THIS

    # GET PRESENT DIAGNOSTICS
    # get the first line of the dataframe
    first_row = df.iloc[0]

    # then, get the diagnostic values associated with that row to compare with the h5
    diags_present = get_diag_values(first_row)

    # this function tells us if we either need to create a new file or overwrite an existing one.
    should_overwrite = check_if_overwrite(desired_path, input_file_path, diags_present)
    #print(should_overwrite)
    # debug line to prevent grid creation
    #return None
    # if the existing diags dataset is the same as the proposed diags, then you are good.
    if not should_overwrite:
        print(f"3d_mesh returning None")
        return None

    check_grid_dir(input_file_path)
    # NOW WE KNOW WE NEED TO CREATE A NEW H5 FILE WITH THE GIVEN NAME
    create_grid_h5(file_name=desired_path, res=res) # this will replace any existing files with this name

    # FILL H5
    with h5py.File(desired_path, 'r+') as f: # we give read and write perms
        # FILL DIAGNOSTICS
        # diagnostic order needs to be diameter, current, offset
        f['/src/diags'][:] = np.array((diags_present['diameter'],diags_present['current'],diags_present['offset'] ),
                                     dtype=dtype_diags)
        # FILL DATA!
        # step 1: assemble the meshgrid
        #   - X, Y, Z lims are the 'offset' value of the diags
        pad = diags_present['offset'] * 1.5
        _ax_linspace = np.linspace(-pad, pad, res)

        grid = np.meshgrid(_ax_linspace, _ax_linspace, _ax_linspace, indexing='ij')
        # fill the coords dataset before moving axis
        f['/src/coords'][:] = grid

        grid = np.moveaxis(grid, 0, -1)

        output = method(grid, **kwargs) # plug in the created meshgrid into the provided method

        # we expect the output to be (100, 100, 100, 3)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # reshape output to (3, 100, 100, 100)
        output_moved = output
        if output.shape == (res,res,res, 3):
            output_moved = np.moveaxis(output, -1, 0)
        f['/src/data'][:] = output_moved


if __name__ == '__main__':
    import magpylib as mp
    from Gui_tkinter.funcs.GuiEntryHelpers import tryEval
    # Run a hardcoded example to test h5 file creation
    filepath = 'D:\\FromCDocuments\\Boris_Usr\\Inputs\\CoilConfigurations\\mirror_10k'
    collection = File_to_Collection(filepath, 'mirror_10k', {"Amp": tryEval, "RotationAngle": tryEval, "RotationAxis": tryEval})
    method = collection.getB

    precalculate_3d_grid(method, Path(filepath))

    #mp.show(collection)
import h5py
from files.PusherClasses import position_dt, velocity_dt, field_b_dt, field_e_dt

"""
Place to define the file structure of the output HDF5 file
"""
def create_h5_output_file(file_name, length, **kwargs):
    """
    Explanation of h5py construction:
    https://docs.h5py.org/en/stable/high/dataset.html#reading-writing-data

    chunks=True tells h5py to make the h5 file use HDF5's chunked storage layout, which splits datasets into
    multiple pieces on the disk. You can specify each chunk's shape, but setting it to True instead tells h5py
    to use its best guess.
    """
        # CREATE FILE, ROOT GROUP
    f = h5py.File(file_name, 'w', libver='latest')
    f.swmr_mode = True # single writer, multiple readers.

        # CREATE BASE GROUP
    grp = f.create_group('/src')

        # THINGS INSIDE THE SRC GROUP
    grp_ds = f.create_dataset("/src/position", (0,), chunks=True, maxshape=(None,), dtype=position_dt) # px, py, pz
    grp_ds2 = f.create_dataset("/src/velocity", (0,), chunks=True, maxshape=(None,), dtype=velocity_dt) # vx, vy, vz, vperp, vpar, vmag
    grp_grp = f.create_group('/src/fields')
    grp_grp_ds = f.create_dataset("/src/fields/b", (0,), chunks=True, maxshape=(None,), dtype=field_b_dt) # bx, by, bz, bmag, bhat
    grp_grp_ds2 = f.create_dataset("/src/fields/e", (0,), chunks=True, maxshape=(None,), dtype=field_e_dt)  # bx, by, bz, eperp, epar, emag

if __name__ == "__main__":
    h5py.run_tests()
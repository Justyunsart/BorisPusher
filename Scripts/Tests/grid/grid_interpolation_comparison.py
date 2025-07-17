
"""
Compare how interpolation holds up to the analytic equation with an existing 3d grid
"""
import h5py
import matplotlib.pyplot as plt
import numpy as np
from Gui_tkinter.funcs.GuiEntryHelpers import File_to_Collection, tryEval
from scipy.interpolate import RegularGridInterpolator

# hard coded location to h5 file
file = 'hexahedron_100K_1.7'
h5_path = f'D:\\FromCDocuments\\Boris_Usr\\Inputs\\CoilConfigurations\\grid\\{file}.hdf5'
filepath =f'D:\\FromCDocuments\\Boris_Usr\\Inputs\\CoilConfigurations\\{file}'

# EXTRACT UNIVERSALLY REQUIRED INFO
# read the specified grid values
with h5py.File(h5_path, 'r') as f:
    # both are (3, 100, 100, 100)
    mesh_Bs = np.array(f['src/data'])
    mesh_Bs = np.moveaxis(mesh_Bs, 0, -1)
    mX, mY, mZ = np.array(f['src/coords'])

# get collection from file
collection = File_to_Collection(filepath, file,
                                {"Amp": tryEval, "RotationAngle": tryEval, "RotationAxis": tryEval})

# we also need to understand the linspace the grid uses. Because it's uniform, we just need to check one axis.
mesh_linspace = mX[:,0,0]

# with everything defined, we can create the interpolator.
#    - assumes indexing='ij', which it is.
#print(mesh_Bs.shape)
mesh_interpolator = RegularGridInterpolator((mesh_linspace, mesh_linspace, mesh_linspace), mesh_Bs)

def evaluate_midpoints(axes=1):
    """
    :param axes: int <= 3; the number of axes to generate midpoints for when interpolating.
    """
    def generate_midpoints(ax:int, ):
        """
        Return an n, 3 array of points representing locations to interpolate to.
        """
        _x, _y, _z = np.meshgrid(mesh_linspace, mesh_linspace, mesh_linspace, indexing='ij')
        axes = [_x, _y, _z]
        # because the grid is assumed to be uniform, we can perform the interpolation once and assign it
        # to the number of axes necessary
        linspace_midpoints = (_x[:-1] - _x[1:]) / 2 # midpoints = avg. of consecutive vals

        for i in range(ax-1):
            axes[i] = linspace_midpoints

        return np.column_stack((_x.ravel(), _y.ravel(), _z.ravel()))

    # Generate the points to evaluate the interpolated and analytic solutions
    points = generate_midpoints(axes)

    analytic_results = collection.getB(points).reshape(3, 100, 100, 100) # Get the analytic results
    interpolated_results = mesh_interpolator(points).reshape(3, 100, 100, 100) # Get the interpolated results

    return analytic_results, interpolated_results, points.reshape(3, 100, 100, 100)

def graph_interpolation_results(analytic_results, interpolated_results, points):
    """
    Holds a series of graphing functions to examine interpolation results.
    """
    fig, ax = plt.subplots()

    def perc_error_contour(analytic_results, interpolated_results, points, y_ind=50):
        """
        |estimated - actual| / actual
        displayed for the XZ cross-section at any given index of Y
        """
        # get the cross-section
        analytic_cross = np.linalg.norm(analytic_results[:, :, y_ind, :], axis=0)
        interpolated_cross = np.linalg.norm(interpolated_results[:, :, y_ind, :], axis=0)

        # calculate percent error
        perc_err_cross = np.abs(analytic_cross - interpolated_cross) / np.abs(analytic_cross)
        #print(perc_err_cross.shape)

        contour = ax.contourf(points[0, :, y_ind, :], points[2, :, y_ind, :], perc_err_cross, cmap='jet', levels=100)
        fig.colorbar(contour)
        ax.set_title(f"Perc. error at XZ cross-section at Y = {points[1, 0, y_ind, 0]}")

    def perc_error_box(analytic_results, interpolated_results, points):
        # get the magnitudes to compare
        analytic_mag = np.linalg.norm(analytic_results[:, :, : :], axis=0)
        interpolated_mag = np.linalg.norm(interpolated_results[:, :, : :], axis=0)

        perc_err = np.abs((np.abs(analytic_mag - interpolated_mag)) / analytic_mag).ravel()
        #print(perc_err.shape)
        boxplot = ax.hist(perc_err, bins=100)

    #perc_error_contour(analytic_results, interpolated_results, points)
    perc_error_box(analytic_results, interpolated_results, points)
    plt.show()



if __name__ == '__main__':
    actual, interpolated, points = evaluate_midpoints(axes=3)
    #print(actual.shape)
    #print(interpolated.shape)

    graph_interpolation_results(analytic_results=actual, interpolated_results=interpolated, points=points)
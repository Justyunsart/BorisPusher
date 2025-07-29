import h5py
import matplotlib.pyplot as plt
import numpy as np
from Gui_tkinter.funcs.GuiEntryHelpers import File_to_Collection, tryEval

"""
Test whether the preconfigured B grid produces the right values
"""

# hard coded location to h5 file
#h5_path = 'D:\\FromCDocuments\\Boris_Usr\\Inputs\\CoilConfigurations\\grid\\hexahedron_100K_1.7.hdf5'
h5_path = "D:\\FromCDocuments\\Boris_Usr\\Inputs\\bob_e\\grid\\SDINGLE.hdf5"
filepath ='D:\\FromCDocuments\\Boris_Usr\\Inputs\\CoilConfigurations\\hexahedron_100K_1.7'

def graph_cross_file():
    # read file
    with h5py.File(h5_path, 'r') as f:
        # both are (3, 100, 100, 100)
        Bs = np.array(f['src/data'])
        X, Y, Z = np.array(f['src/coords'])

    Bx, By, Bz = Bs
    # we want to graph the XZ plane at Y ~ 0.
    B_mags = np.log(np.linalg.norm(Bs, axis=0))

    fig, ax = plt.subplots()
    contour = ax.contourf(X[:,50,:], Z[:,50,:], B_mags[:,50,:], levels=100)
    fig.colorbar(contour)

    streamline = ax.streamplot(X[:,50,50], Z[50,50,:], Bx[:, 50, :].T, Bz[:, 50, :].T)
    #fig.colorbar(streamline.lines)
    ax.set_title("MESHGRID B FIELD ON THE XZ PLANE")

def graph_cross_analytic():
    # get collection from file
    collection = File_to_Collection(filepath, 'hexahedron_100K_1.7',
                                    {"Amp": tryEval, "RotationAngle": tryEval, "RotationAxis": tryEval})
    # make grid
    lim = 1.1 * 1.1
    ax_lin = np.linspace(-lim, lim, 100)
    grid = np.meshgrid(ax_lin, ax_lin, ax_lin, indexing='ij')
    X, Y, Z = grid
    grid = np.moveaxis(grid, 0, -1)

    Bs = collection.getB(grid)
    Bs = np.moveaxis(Bs, -1, 0)

    Bx, By, Bz = Bs

    # we want to graph the XZ plane at Y ~ 0.
    B_mags = np.log(np.linalg.norm(Bs, axis=0))


    fig, ax = plt.subplots()
    contour = ax.contourf(X[:, 50, :], Z[:, 50, :], B_mags[:, 50, :], levels=100)
    fig.colorbar(contour)
    streamline = ax.streamplot(ax_lin, ax_lin, Bx[:,50,:].T, Bz[:,50,:].T)
    #fig.colorbar(streamline.lines)
    ax.set_title("ANALYTIC B FIELD ON THE XZ PLANE")


if __name__ == '__main__':
    graph_cross_file()
    #graph_cross_analytic()

    plt.show()
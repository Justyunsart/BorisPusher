from EFieldFJW.fwysr_2 import fwysr_2
import matplotlib.pyplot as plt
import numpy as np
from magpylib import Collection
from magpylib.current import Circle
import matplotlib as mpl
from Alg.polarSpace import toCyl, toCart
from EFieldFJW.streamlines3Dring import compute_field

# Create testing collection
c1 = Circle(position=np.array([0, 0, 0]), diameter=2, current=1e-11)
c1.rotate_from_angax(90, "x")
#c2 = Circle(position=np.array([0, 0, 0]), diameter=2, current=1e-11)
#c2.rotate_from_angax(90, "x")
collection = Collection(c1)

"""
It's not going to be the exact same as the above, but gonna be the same idea
"""
def rho_range_contour():
    fig, (ax, ax1) = plt.subplots(1,2, sharey=False)
    lim = 1.25
    # construct grid for cross-section
    x = np.linspace(-lim, lim, 100)
    y = np.linspace(-lim, lim, 100)
    z = np.ones(1) * 0.1

    X, Y, Z = np.array(np.meshgrid(x, y, z, indexing='xy')) # shape = (3, 100, 100, 1)
    #grid = np.moveaxis(grid, 0, 0)[0]
    #print(grid.shape)
    # X, Y, Z = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)
    grid = np.stack([X, Y, Z], axis=-1)  # Shape: (Nx, Ny, Nz, 3)
    grid = grid.reshape(-1, 3)  # Flatten to shape (Nx * Ny * Nz, 3)

    mags = []
    Ex = []
    Ey = []
    Erho = []
    Ezeta = []
    for coord in grid:
        _sum = []
        for ring in collection:
            # transform coordinate
            _coord = ring.orientation.apply(np.array(coord - ring.position), inverse=True)
            # turn coordinate to terms of cyl
            _coord = toCyl(_coord)

            # plug it in to the solution
            #frho, fzeta = fwysr_2(ring.current, ring.diameter/2, _coord)
            frho, fzeta = compute_field(_coord[0], _coord[2])
            #print(frho.dtype)
            if (np.isnan(frho)):
                print(_coord)
            Erho.append(frho)
            Ezeta.append(fzeta)

            # turn solution back to cartesian
            _coord = toCart(frho, _coord[1], fzeta)
            # re-rotate the point
            _coord = ring.orientation.apply(_coord, inverse=False)
            _sum.append(_coord)
        E = np.array(_sum).sum(axis=0) # get columnwise sums from each ring
        #print(E)
        mags.append(np.linalg.norm(E))
        Ex.append(E[0])
        Ey.append(E[1])
    mags = np.array(np.log(mags)).reshape(100, 100)
    Erho = np.log(np.abs(np.array(Erho))).reshape(100, 100)
    Ezeta = np.log(np.abs(np.array(Ezeta))).reshape(100, 100)
    cmap = plt.get_cmap('turbo')
    norm = mpl.colors.Normalize()
    contour=ax.contourf(X[:,:,0], Y[:,:,0], mags, levels=100, cmap=cmap, norm=norm)
    ax.streamplot(X[:,:,0],Y[:,:,0], np.array(Ex).reshape(100,100), np.array(Ey).reshape(100,100), color='black')
    fig.colorbar(contour, ax=ax)

    lines = ax1.plot(y, mags[50][:], label='Magnitude')
    ax1.plot(y, np.array(Erho)[50][:], label='Rho')
    ax1.plot(y, np.array(Ezeta)[50][:], label='Zeta')
    ax1.legend()


if __name__ == '__main__':
    rho_range_contour()
    plt.show()

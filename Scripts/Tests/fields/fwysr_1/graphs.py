from EFieldFJW.fwysr_e_1 import feysr_e_1
import matplotlib.pyplot as plt
import numpy as np
from magpylib import Collection
from magpylib.current import Circle
import matplotlib as mpl
from Alg.polarSpace import toCyl, toCart

# Create testing collection
c1 = Circle(position=np.array([0, 0, 0]), diameter=2, current=1e-11)
#c1.rotate_from_angax(90, "y")
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
    z = np.ones(1) * 0.01

    grid = np.array(np.meshgrid(x, y, z, indexing='ij')).T  # shape = (3, 100, 100, 1)
    grid = np.moveaxis(grid, 0, 0)[0]
    #print(grid.shape)
    X, Y, Z = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)
    grid = grid.reshape(100 ** 2, 3)

    mags = []
    Ex = []
    Ey = []
    for coord in grid:
        _sum = []
        for ring in collection:
            # transform coordinate
            _coord = ring.orientation.apply(np.array(coord - ring.position), inverse=True)
            # turn coordinate to terms of cyl
            _coord = toCyl(_coord)

            # plug it in to the solution
            fzeta, frho = feysr_e_1(_coord[0], _coord[2], ring.diameter/2, ring.current)

            # turn solution back to cartesian
            _coord = toCart(frho, _coord[1], fzeta)
            # re-rotate the point
            _coord = ring.orientation.apply(_coord, inverse=False)
            _sum.append(_coord)
        E = np.array(_sum).sum(axis=0) # get columnwise sums from each ring
        print(E)
        mags.append(np.linalg.norm(E))
        Ex.append(E[0])
        Ey.append(E[1])
    mags = np.array(np.log(mags)).reshape(100, 100)
    cmap = plt.get_cmap('turbo')
    norm = mpl.colors.Normalize()
    cbarticks = np.arange(-8.0, 8.0, 0.5)
    contour=ax.contourf(X, Y, mags, levels=cbarticks, cmap=cmap, norm=norm)
    ax.streamplot(X,Y, np.array(Ex).reshape(100,100), np.array(Ey).reshape(100,100), color='black')
    fig.colorbar(contour, ax=ax, ticks=cbarticks)

    lines = ax1.plot(y, mags[50][:])

if __name__ == '__main__':
    rho_range_contour()
    plt.show()

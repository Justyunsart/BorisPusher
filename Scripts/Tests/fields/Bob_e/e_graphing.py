import matplotlib.pyplot as plt
import numpy as np
from Alg.polarSpace import toCyl, toCart
import matplotlib as mpl


def at(coord, q=1, radius=1, resolution=100):
    """
    implementation of the function.
    Inputs:
    q: total charge of the ring in Coulombs
    """
    # print(f"q is: {q}")
    # print(f"coord is: {coord}")
    # print(f'FieldMethods_Impl.bob_e_impl.at: bob_e called with charge {q} and radius {radius}')
    # Parameters
    k = 8.99e9  # Coulomb's constant, N * m^2/C^2
    kq_a2 = (k * q) / (radius ** 2)

    # Coordinate Constants
    zeta = coord[2] / radius
    rho = coord[0] / radius
    if rho == 0:
        rho = 0.00001

    # Integral Constants - pg.3 of document
    mag = (rho ** 2 + zeta ** 2 + 1)
    mag_3_2 = mag ** (3 / 2)
    ## Fzeta
    Fzeta_c = (zeta) / (mag_3_2 * (radius ** 2))
    ## Frho
    Frho_c = (rho) / (mag_3_2 * (radius ** 2))

    # Integration
    # Circle is broken into {resolution} slices; with each result being appended to the lists below.

    thetas = np.linspace(0, np.pi,
                         resolution)  # np.array of all the theta values used in the integration (of shape {resolution})
    cosines = np.cos(thetas)  # np.array of all the cosine values of the thetas
    denominators = (1 - ((2 * rho * cosines) / mag)) ** (3 / 2)  # shared denominator values of fzeta and frho

    # replace zeros with a really small decimal.
    denominators[denominators == 0] = 1e-20

    fzeta = 1 / denominators
    frho = (1 - cosines / rho) / denominators

    # Final - fzeta, frho is summed, multiplied by the integration constant and kq.a^2.
    zeta = np.asarray(fzeta).sum() * Fzeta_c * kq_a2
    rho = np.asarray(frho).sum() * Frho_c * kq_a2
    return zeta, rho

def test_rho_range():
    fig, ax = plt.subplots()
        # Create a bunch of cylindrical coordinates
            # generate rho values in a linspace
    _rh = np.linspace(-2, 2, 100)
            # zeta value is a constant. theta is unused. both will be 0s
    _z = np.ones(shape=(100))
    _th = np.zeros(shape=(100))
    coords = np.column_stack((_rh, _th, _z))

    mags = []
    for coord in coords:
        zeta, rho = at(coord)
        mags.append(np.sqrt(rho ** 2 + zeta ** 2))

    ax.plot(_rh, mags)
    #plt.show()

"""
It's not going to be the exact same as the above, but gonna be the same idea
"""
def test_rho_range_cart():
    fig, ax = plt.subplots()
    _x = np.linspace(-2, 2, 100)
    _y = np.zeros(shape=(100))
    _z = np.ones(shape=(100))
    coords = np.column_stack((_x, _y, _z))
    mags = []
    for coord in coords:
        c = toCyl(coord)
        zeta, rho = at(c)
        mags.append(np.sqrt(rho ** 2 + zeta ** 2))
    ax.plot(_x, mags)
    #plt.show()

"""
It's not going to be the exact same as the above, but gonna be the same idea
"""
def test_rho_range_contour():
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
        c = toCyl(coord)
        #print(c)
        zeta, rho = at(c, resolution=200, q=(1e-11/200))
        mags.append(np.sqrt(rho ** 2 + zeta ** 2))
        cart = toCart(rho, c[1], z)
        Ex.append(cart[0])
        Ey.append(cart[1])
    mags = np.log(np.array(mags).reshape(100, 100))
    #print(mags)
    cmap = plt.get_cmap('turbo')
    norm = mpl.colors.Normalize(vmin=-8, vmax=8)
    cbarticks = np.arange(-8.0, 8.0, 0.5)
    contour=ax.contourf(X, Y, mags, levels=cbarticks, cmap=cmap, norm=norm, vmin=-8, vmax=8)
    ax.streamplot(X,Y, np.array(Ex).reshape(100,100), np.array(Ey).reshape(100,100), color='black')
    ax.set_title('Bob_e horizontal ring')
    fig.colorbar(contour, ax=ax, ticks=cbarticks)

    # lineout at i=50 (when x is a small value approaching 0)
    lines = ax1.plot(y, mags[50][:])

def test_grid_creation():
    fig, ax = plt.subplots()
    lim = 2
    # construct grid for cross-section
    x = np.linspace(0, lim * 2, 100)
    z = np.linspace(0, lim * 2, 100)
    y = np.array(np.ones(100) * lim)

    grid = np.array(np.meshgrid(x, y, z)).T  # shape = (100, 100, 3, 1)
    grid = np.moveaxis(grid, 2, 0)[0]  # shape = (100, 100, 3)
    X, _, Z = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)
    X = X-(lim)
    Z = Z-(lim)

    ax.scatter(X, Z)
    #plt.show()

if __name__ == '__main__':
    #test_grid_creation()
    test_rho_range_contour()
    plt.show()
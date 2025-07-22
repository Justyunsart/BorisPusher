import numpy as np
from Alg.polarSpace import toCyl
import magpylib as mp
from magpylib import Collection
from magpylib.current import Circle


def bob_e_at(coord, q=1, radius=1, resolution=100, convert=True):
    """
    Vectorized version of bob_e_at with proper numerical integration.
    Inputs:
        coord: ndarray of shape (3, Nx, Ny, Nz) in cylindrical coordinates (r, θ, z)
        q: total charge
        radius: coil radius
        resolution: number of integration points
    Returns:
        zeta, rho: electric field components along z and r directions, shape (Nx, Ny, Nz)
    """
    k = 8.99e9  # Coulomb's constant
    kq_a2 = (k * q) / (radius ** 2)

    rho = coord[0] / radius  # (Nx, Ny, Nz)
    zeta = coord[2] / radius

    mag = rho ** 2 + zeta ** 2 + 1
    mag_3_2 = mag ** 1.5

    Fzeta_c = zeta / (mag_3_2 * radius ** 2)
    Frho_c = rho / (mag_3_2 * radius ** 2)

    # Integration setup
    thetas = np.linspace(0, np.pi, resolution)
    dtheta = thetas[1] - thetas[0]
    cosines = np.cos(thetas).reshape((-1, 1, 1, 1))  # (res, 1, 1, 1)

    # Broadcast spatial coords
    rho_exp = rho[None, :, :, :]
    mag_exp = mag[None, :, :, :]

    denom = (1 - (2 * rho_exp * cosines / mag_exp)) ** 1.5
    denom = np.where(denom == 0, 1e-20, denom)

    # Safe rho to avoid div-by-zero
    rho_safe = np.where(np.abs(rho_exp) < 1e-8, 1e-8, rho_exp)

    # Integrate
    fzeta = np.sum((1 / denom) * dtheta, axis=0)
    frho = np.sum(((1 - cosines / rho_safe) / denom) * dtheta, axis=0)

    # Scale
    E_zeta = fzeta * Fzeta_c * kq_a2
    E_rho = frho * Frho_c * kq_a2

    return E_zeta, E_rho

def bob_e_from_collection(grid, collection:Collection):
    # grid is assumed to be (n, n, n, 3) shaped
    _coords = grid.reshape(-1, 3) # shape: (N,3)
    #_coords = np.column_stack([grid[0].ravel(), grid[1].ravel(), grid[2].ravel()])

    output_grid = np.zeros((100, 100, 100, 3), dtype=np.float64)
    for coil in collection.children_all:
        # looping over each coil is better than looping over all points in the meshgrid
        # First, rotate all points in the provided grid
        coords = coil.orientation.apply(_coords, inverse=True)
        #   reshape back
        coords = coords.reshape((100, 100, 100, 3))

        # convert all parts of the grid into cylindrical
        # Assume 'grid' is shaped (3, 100, 100, 100) = (x, y, z)
        x, y, z = np.moveaxis(coords, -1, 0)

        # Cylindrical conversion
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        z_cyl = z  # z remains the same

        # Stack if needed: shape (3, 100, 100, 100)
        cylindrical_grid = np.stack((r, theta, z_cyl), axis=0)

        print("cylindrical_grid.shape:", cylindrical_grid.shape)

        zeta, rho = bob_e_at(cylindrical_grid, q=coil.current, radius=coil.diameter/2, resolution=200, convert=False)

        # convert back to cartesian
        x = rho * np.cos(theta)
        y = rho * np.sin(theta)
        z = zeta

        cartesian_grid = np.stack((x, y, z), axis=0)

        # we need to apply the forward rotation of the coil before done
        _out = cartesian_grid.reshape(-1, 3)
        #_out = np.column_stack([cartesian_grid[0].ravel(), cartesian_grid[1].ravel(), cartesian_grid[2].ravel()])
        out = coil.orientation.apply(_out, inverse=False)
        out = out.reshape((100, 100, 100, 3))

        output_grid += out

    #output_grid = np.moveaxis(output_grid, 0, -1)
    return output_grid

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    # Grid setup
    Nx = Ny = Nz = 100
    x = np.linspace(-2, 2, Nx)
    y = np.linspace(-2, 2, Ny)
    z = np.linspace(-2, 2, Nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Cylindrical coords
    R = np.sqrt(X ** 2 + Y ** 2)
    Theta = np.arctan2(Y, X)
    cyl_grid = np.stack((R, Theta, Z), axis=0)

    # Compute field
    Ez, Erho = bob_e_at(cyl_grid, q=1.0, radius=1.0, resolution=200)
    Ex = Erho * np.cos(Theta)
    Ey = Erho * np.sin(Theta)

    # Magnitude and cross section
    Emag = np.sqrt(Ex ** 2 + Ey ** 2 + Ez ** 2)
    cross_section = Emag[:, Ny // 2, :]  # XZ plane

    # Plot
    plt.imshow(cross_section, extent=(-2, 2, -2, 2))
    plt.title("E Field Cross Section (XZ plane)")
    plt.colorbar()
    plt.show()
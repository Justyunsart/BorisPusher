import numpy as np
import matplotlib.pyplot as plt
import magpylib as mp
from Alg.polarSpace import toCyl, toCart
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Physical constants and parameters
epsilon_0 = 8.854e-12  # Vacuum permittivity (F/m)
#Q = 1e-11               # Total charge on the ring (Coulombs)
#a = 1.0                # Radius of the ring (meters)
#lambda_ = Q / (2 * np.pi)  # Linear charge density


def _compute_field(point, num_points, coil):
    """
    Gets the E-field given a point in cyl coordinates and a single coil.
    This is the function that is run in the threadpool
    """
    def make_dimensionless_inputs(r, z, radius):
        return r / radius, z / radius

    # Define the electric field components
    def integrand_Er(theta, r, z):
        D = np.sqrt(r ** 2 + 1 - 2 * r * np.cos(theta) + z ** 2)
        return (r - np.cos(theta)) / D ** 3

    def integrand_Ez(theta, r, z):
        D = np.sqrt(r ** 2 + 1 - 2 * r * np.cos(theta) + z ** 2)
        return 1 / D ** 3

    # orient the point to the given coil
    rotated_coord = coil.orientation.apply((point - coil.position), inverse=True)  # rotation
    cyl_coord = toCyl(rotated_coord)

    # get coil constants
    charge = coil.current
    radius = coil.diameter / 2
    lambda_ = charge / (2 * np.pi)  # Linear charge density
    r, z = make_dimensionless_inputs(cyl_coord[0], cyl_coord[2], radius)

    # vectorized integral
    theta = np.linspace(0, 2 * np.pi, num_points)  # generate thetas
    dtheta = theta[1] - theta[0]  # linear rate of change for thetas
    int_Er = np.sum(integrand_Er(theta, r, z)) * dtheta
    int_Ez = np.sum(integrand_Ez(theta, r, z)) * dtheta
    E_r = (1 / (4 * np.pi * epsilon_0)) * lambda_ * int_Er
    E_z = (1 / (4 * np.pi * epsilon_0)) * lambda_ * z * int_Ez

    # convert back to cart.
    raw_E = np.array(toCart(E_r, cyl_coord[1], E_z))

    return coil.orientation.apply(raw_E, inverse=False)


def compute_field(field_coord, coils:mp.Collection, num_points=500, executor=None):
    """
    A literal implementation of a uniformly charged ring's e-field from an arbitrary point.
    Takes in a specific set of inputs:

    field_coord: iterable (3) representing the point to get the E field at
    coils: a magpylib.Collection object representing the coil configuration.
        > This function iterates over this collection to get the total summed E
    num_points: an int representing the number of points to use in the integration
    executor: a concurrent.futures.ThreadPoolExecutor object, if provided, will be used.
        > Executor needs to be provided and is not created so the number of executors is controlled.

    """
    # preallocate output array
    Es = np.empty((len(coils), 3), dtype=np.float64)

    i = 0 # iterator
    # default behavior; just loop over all the coils in the collection
    if executor is None:
        for coil in coils:
            Es[i, :] = _compute_field(field_coord, coil, num_points)
            i += 1 # increment iteration

    # if given an executor, submit workers to it instead.
    elif type(executor) is ThreadPoolExecutor:
        futures = executor.map(partial(_compute_field, field_coord, num_points), coils)
        for future in futures:
            Es[i, :] = future
            i += 1

    return np.sum(Es, axis=0) # sum all the results from the coils columnwise

if __name__ == '__main__':
    # Grid setup in r-z plane
    r_vals = np.linspace(0.1, 2.0, 40)
    z_vals = np.linspace(-2.0, 2.0, 40)
    R, Z = np.meshgrid(r_vals, z_vals)

    # Compute field components
    E_r = np.zeros_like(R)
    E_z = np.zeros_like(Z)

    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            E_r[i, j], E_z[i, j] = compute_field(R[i, j], Z[i, j])

    # Streamplot requires 2D Cartesian grid
    X = R
    Y = Z
    U = E_r
    V = E_z

    # Plot streamlines
    fig, ax = plt.subplots(figsize=(10, 6))
    strm = ax.streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='viridis', density=1.2)

    # # Plot the ring in r-z plane (circular ring at z=0)
    # theta_ring = np.linspace(0, 2 * np.pi, 200)
    # ring_x = a * np.cos(theta_ring)
    # ring_y = a * np.sin(theta_ring)
    # ax.plot(ring_x, ring_y, 'r', linewidth=2, label='Ring of Charge')

    # Define the x values for the line
    x_values = [-1, 1]
    # Define the y values (constant at 0 for a horizontal line)
    y_values = [0, 0]

    # Plot the line
    ax.plot(x_values, y_values, color='red', linewidth=4, label="Ring of Charge")

    # Labels and formatting
    ax.set_title('Electric Field Streamlines of a Ring of Charge (2D slice)')
    ax.set_xlabel('r (m)')
    ax.set_ylabel('z (m)')
    ax.legend()
    fig.colorbar(strm.lines, ax=ax, label='Electric Field Magnitude (a.u.)')
    ax.axis('equal')
    ax.grid(True)
    plt.tight_layout()
plt.show()

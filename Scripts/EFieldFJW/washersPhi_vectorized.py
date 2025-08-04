import numpy as np
from scipy.constants import epsilon_0
from scipy.special import ellipk
from scipy.integrate import simpson


def rotation_matrix_from_vectors(vec1, vec2):
    """Find rotation matrix that aligns vec1 to vec2."""
    a = vec1 / np.linalg.norm(vec1)
    b = vec2 / np.linalg.norm(vec2)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.allclose(c, 1):
        return np.eye(3)
    if np.allclose(c, -1):
        axis = np.array([1, 0, 0]) if not np.allclose(a, [1, 0, 0]) else np.array([0, 1, 0])
        return rotation_matrix_from_axis_angle(axis, np.pi)
    s = np.linalg.norm(v)
    kmat = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / s ** 2)


def rotation_matrix_from_axis_angle(axis, angle):
    """Rodrigues' rotation formula."""
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1 - c
    return np.array([
        [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, c + z * z * C]
    ])


def phi_disk_at_points(r_points, center, normal, sigma, Q, a, b, r_res=200):
    """
    Vectorized scalar potential from a single charged disk at many points.

    Parameters:
    - r_points: (N, 3) array of N field points
    - center: (3,) center of the disk
    - normal: (3,) normal vector of the disk plane
    - Q: total charge
    - a, b: inner and outer radii
    - r_res: resolution of radial integration

    Returns:
    - phi_vals: (N,) array of potential values
    """
    if not sigma:
        sigma.append(Q / (np.pi * (b ** 2 - a ** 2)))
    sigma = sigma[0] # update internal sigma variable with the stored value.

    r_points = np.atleast_2d(r_points)  # shape (N, 3)
    N = r_points.shape[0]

    # Charge density
    #sigma = Q / (np.pi * (b ** 2 - a ** 2))

    # Rotation matrix to align normal to z-axis
    Rmat = rotation_matrix_from_vectors(normal, np.array([0, 0, 1]))

    # Transform field points into local disk coordinates
    rel_points = r_points - center
    r_local = (Rmat @ rel_points.T).T  # shape (N, 3)

    rho = np.linalg.norm(r_local[:, :2], axis=1)  # shape (N,)

    #print(rho.shape)

    z = r_local[:, 2]  # shape (N,)

    # Avoid division by zero at the disk center
    mask = (rho == 0) & (z == 0)
    rho[mask] = 1e-12
    z[mask] = 1e-12

    #print(rho.shape)

    # Prepare integration
    R_vals = np.linspace(a, b, r_res)  # shape (r_res,)
    #print(R_vals)
    R_grid, rho_grid = np.meshgrid(R_vals, rho, indexing='ij')  # shape (r_res, N)
    z_grid = z[None, :]  # shape (1, N)

    #print(R_grid.shape)

    k2 = 4 * R_grid * rho_grid / ((R_grid + rho_grid) ** 2 + z_grid ** 2)
    k2 = np.clip(k2, 0, 1 - 1e-12)

    #print(k2.shape)
    K = ellipk(k2)

    denom = np.sqrt((R_grid + rho_grid) ** 2 + z_grid ** 2)
    integrand = R_grid * K / denom
    #print(integrand.shape)

    # Simpson integration over R_vals (axis=0)
    result = simpson(integrand, x=R_vals, axis=0)  # shape (N,)
    phi_vals = sigma / (2 * epsilon_0) * result

    # Set potential to 0 where rho==0 and z==0 (if any)
    phi_vals[mask] = 0

    return phi_vals

def washer_phi_from_collection(points, collection, inners, normals, sigmas, r_res=200, nump=10):
    """
    interfaces with magpy4c1.py's inputs
    """
    _sum = np.empty((points.shape[0],))
    for i in range(len(collection)):
        print(f"starting work on ring: {i}")
        ring = collection[i]
        position = ring.position
        _sum += phi_disk_at_points(points, position, normals[i],
                                    sigmas[i], abs(ring.current), inners, ring.diameter/2, r_res)
    return _sum

if __name__ == "__main__":
    # visualize cross section of E field

    import matplotlib.pyplot as plt
    from MakeCurrent import Helmholtz
    from MakeCurrent import Circle as Hex
    import numpy as np

    # create washer containers
    b = 0.75
    a = 0.25
    d = 1

    #collection = Helmholtz(1e-11, b, d)
    #collection.rotate_from_angax(90, 'x')
    collection = Hex(1e-11, b, d, gap=0)  # collection = container for all the washers
    #inners = [a, a]  # corresponding inner washer rho
    # collect coil information
    normals = []  # input n_coils amount of (3,) arrays
    sigmas = []  # input n_coils amount of empty lists
    for ring in collection.children_all:
        # we can get the coil's normal by rotating [0, 0, 1] by the coil's orientation.
        default_z = np.array([0, 0, 1])
        normals.append(ring.orientation.apply(default_z))

        # append empty list per coil into sigmas
        sigmas.append([])

    # create (n, 3) array of points
    lim = 2
    res = 101
    _lin = np.linspace(-lim, lim, res)
    _x, _y, _z = np.meshgrid(_lin, _lin, _lin, indexing='ij')
    points = np.stack([_x.ravel(), _y.ravel(), _z.ravel()], axis=-1)

    # compute results
    potentials = np.array(washer_phi_from_collection(points, collection, a, normals, sigmas))
    potentials = np.reshape(potentials, (res, res, res))
    #print(potentials.shape)

    # graph cross section (streamline)
    fig, ax = plt.subplots()

    # Compute electric field: E = -∇Φ
    dax = _lin[1] - _lin[0]
    # Ex, Ez = -np.gradient(phi_grid, dx, dz)
    dphi_dx, dphi_dy, dphi_dz = np.gradient(potentials, dax, dax, dax)
    Ex = -dphi_dx
    Ez = -dphi_dz
    Ey = -dphi_dy

    #print(Ex.shape)
    ind = res // 2
    stream = ax.streamplot(_lin, _lin, Ex[:, :, ind].T, Ey[:, : , ind].T)

    #colorbar = fig.colorbar(stream.lines, ax=stream)
    plt.grid(True)
    #plt.axis('equal')

    plt.plot([a, b], [d, d], color='green', linewidth=6, label="Charged Conductor")
    plt.plot([a, b], [-d, -d], color='green', linewidth=6, label="Charged Conductor")
    plt.plot([-a, -b], [-d, -d], color='green', linewidth=6, label="Charged Conductor")
    plt.plot([-a, -b], [d, d], color='green', linewidth=6, label="Charged Conductor")

    # Z-oriented disks: centers at z = ±offset, x = 0
    plt.plot([d, d], [a, b], color='green', linewidth=6, label="Disk +z")  # at z = +0.5
    plt.plot([d, d], [-a, -b], color='green', linewidth=6, label="Disk +z")  # at z = +0.5
    plt.plot([-d, -d], [a, b], color='green', linewidth=6, label="Disk -z")  # at z = -0.5
    plt.plot([-d, -d], [-a, -b], color='green', linewidth=6, label="Disk -z")  # at z = -0.5
    plt.show()

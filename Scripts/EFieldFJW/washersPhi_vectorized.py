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


def phi_disk_at_points(r_points, center, normal, Q, a, b, r_res=150):
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
    r_points = np.atleast_2d(r_points)  # shape (N, 3)
    N = r_points.shape[0]

    # Charge density
    sigma = Q / (np.pi * (b ** 2 - a ** 2))

    # Rotation matrix to align normal to z-axis
    Rmat = rotation_matrix_from_vectors(normal, np.array([0, 0, 1]))

    # Transform field points into local disk coordinates
    rel_points = r_points - center
    r_local = (Rmat @ rel_points.T).T  # shape (N, 3)

    rho = np.linalg.norm(r_local[:, :2], axis=1)  # shape (N,)
    z = r_local[:, 2]  # shape (N,)

    # Avoid division by zero at the disk center
    mask = (rho == 0) & (z == 0)
    rho[mask] = 1e-12
    z[mask] = 1e-12

    # Prepare integration
    R_vals = np.linspace(a, b, r_res)  # shape (r_res,)
    R_grid, rho_grid = np.meshgrid(R_vals, rho, indexing='ij')  # shape (r_res, N)
    z_grid = z[None, :]  # shape (1, N)

    k2 = 4 * R_grid * rho_grid / ((R_grid + rho_grid) ** 2 + z_grid ** 2)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)

    denom = np.sqrt((R_grid + rho_grid) ** 2 + z_grid ** 2)
    integrand = R_grid * K / denom  # shape (r_res, N)

    # Simpson integration over R_vals (axis=0)
    result = simpson(integrand, R_vals, axis=0)  # shape (N,)
    phi_vals = sigma / (2 * epsilon_0) * result

    # Set potential to 0 where rho==0 and z==0 (if any)
    phi_vals[mask] = 0

    return phi_vals

def washer_phi_from_collection(point, collection, inners, normals, sigmas, r_res=150):
    """
    interfaces with magpy4c1.py's inputs
    """
    _sum = 0
    for i in range(len(collection)):
        ring = collection[i]
        position = ring.position
        _sum += phi_disk_at_points(point, position, normals[i], ring.current,
                                    inners[i], ring.diameter/2, sigmas[i], r_res)
    return sum

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Washer parameters
    Q = 1e-11
    a, b = 0.25, 0.75
    sigma = Q / (np.pi * (b ** 2 - a ** 2))
    disk_separation = 2.0
    offset = disk_separation / 2
    c = offset
    # Integration grid for radius
    R = np.linspace(a, b, 150)

    # Define six disks: center and normal
    disks = [
        {"center": np.array([offset, 0, 0]), "normal": np.array([-1, 0, 0])},  # +x
        {"center": np.array([-offset, 0, 0]), "normal": np.array([1, 0, 0])},  # -x
        {"center": np.array([0, offset, 0]), "normal": np.array([0, -1, 0])},  # +y
        {"center": np.array([0, -offset, 0]), "normal": np.array([0, 1, 0])},  # -y
        {"center": np.array([0, 0, offset]), "normal": np.array([0, 0, -1])},  # +z
        {"center": np.array([0, 0, -offset]), "normal": np.array([0, 0, 1])},  # -z
    ]


    # Grid (xz-plane slice at y = 0)
    x = np.linspace(-1.5, 1.5, 100)
    z = np.linspace(-1.5, 1.5, 100)
    X, Z = np.meshgrid(x, z)
    Y = np.zeros_like(X)  # slice at y = 0

    # Compute potential field
    phi_grid = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            r = np.array([X[i, j], Y[i, j], Z[i, j]])
            phi_grid[i, j] = total_phi(r)

    # Compute electric field: E = -∇Φ
    dx = x[1] - x[0]
    dz = z[1] - z[0]
    # Ex, Ez = -np.gradient(phi_grid, dx, dz)
    dphi_dz, dphi_dx = np.gradient(phi_grid, dz, dx)
    Ex = -dphi_dx
    Ez = -dphi_dz

    # Streamplot
    plt.figure(figsize=(10, 8))
    strm = plt.streamplot(X, Z, Ex, Ez, color=np.log(np.sqrt(Ex**2 + Ez**2)), cmap='plasma', density=1.4)
    plt.colorbar(strm.lines, label=r'$\log|\vec{E}|$')
    plt.title("Electric Field Streamlines from 6 Inward-Facing Annular Disks (xz-plane)")
    plt.xlabel('x (m)')
    plt.ylabel('z (m)')
    plt.axis('equal')
    plt.grid(True)

    # Disk cross-section thickness for visual representation
    width = [a, b]
    height = [c, c]
    plt.plot([a, b], [c, c], color='green', linewidth=6, label="Charged Conductor")
    plt.plot([a, b], [-c, -c], color='green', linewidth=6, label="Charged Conductor")
    plt.plot([-a,-b], [-c, -c], color='green', linewidth=6, label="Charged Conductor")
    plt.plot([-a,-b], [c, c], color='green', linewidth=6, label="Charged Conductor")

    # Z-oriented disks: centers at z = ±offset, x = 0
    plt.plot([c, c], [ a,  b], color='green', linewidth=6, label="Disk +z")  # at z = +0.5
    plt.plot([c, c], [ -a,  -b], color='green', linewidth=6, label="Disk +z")  # at z = +0.5
    plt.plot([-c, -c], [a, b], color='green', linewidth=6, label="Disk -z")  # at z = -0.5
    plt.plot([-c, -c], [-a, -b], color='green', linewidth=6, label="Disk -z")  # at z = -0.5

    plt.show()
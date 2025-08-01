import numpy as np
from scipy.constants import epsilon_0
from scipy.special import ellipk
from scipy.integrate import simpson

def rotation_matrix_from_axis_angle(axis, angle):
    """Generate a 3x3 rotation matrix from axis and angle (Rodrigues' formula)."""
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1 - c
    return np.array([
        [c + x*x*C,     x*y*C - z*s, x*z*C + y*s],
        [y*x*C + z*s, c + y*y*C,     y*z*C - x*s],
        [z*x*C - y*s, z*y*C + x*s, c + z*z*C]
    ])

def rotation_matrix_from_vectors(vec1, vec2):
    """Find rotation matrix that aligns vec1 to vec2."""
    _a, _b = vec1 / np.linalg.norm(vec1), vec2 / np.linalg.norm(vec2)
    _v = np.cross(_a, _b)
    _c = np.dot(_a, _b)
    if np.allclose(_c, 1):
        return np.eye(3)
    if np.allclose(_c, -1):
        # 180 degree rotation
        axis = np.array([1, 0, 0]) if not np.allclose(a, [1, 0, 0]) else np.array([0, 1, 0])
        return rotation_matrix_from_axis_angle(axis, np.pi)
    s = np.linalg.norm(_v)
    kmat = np.array([
        [0, -_v[2], _v[1]],
        [_v[2], 0, -_v[0]],
        [-_v[1], _v[0], 0]
    ])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / s**2)

def phi_disk_at_point(r_global, center, normal, Q, a, b, _sigma:list=[], r_res:int=150):
    """
    Scalar potential from a single disk at point r_global.

    :params:
    r_global, center: the coordinates of the field point and center of the disk, respectively.
    normal: a matrix (3) representing the normal vector of the disk's aligned plane.
    Q: the disk's charge
    a, b: the inner, outer rho values of the washer
    _sigma: a list containing either None, or the disk's sigma scalar.
    r_res: the number of points to create in the linspace of a and b.

    :returns:
    The scalar potential at the point inputted.
    """
    # COLLECT FACTORS
    #   calculate sigma
    #   stored externally. If it's empty/none, then calculate and populate it.
    #   make this a single item list so that it will be mutuable.
    if not _sigma:
        _sigma.append(Q / (np.pi * (b ** 2 - a ** 2)))
    sigma = _sigma[0] # update internal sigma variable with the stored value.

    #   get the local rho linspace
    R = np.linspace(a, b, r_res)

    # RUN INTEGRAL
    #   Build rotation matrix to align disk normal with +z
    Rmat = rotation_matrix_from_vectors(normal, np.array([0, 0, 1]))
    r_local = Rmat @ (r_global - center)

    rho = np.linalg.norm(r_local[:2])
    z = r_local[2]
    if rho == 0 and z == 0:
        return 0  # avoid singularity

    #   collect modulus for elliptical integral
    k2 = 4 * R[:, None] * rho / ((R[:, None] + rho)**2 + z**2)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)

    denom = np.sqrt((R[:, None] + rho)**2 + z**2)
    integrand = R[:, None] * K / denom
    result = simpson(integrand, R, axis=0)
    phi_val = sigma / (2 * epsilon_0) * result

    return phi_val.item()

def total_phi(r_point):
    """Sum scalar potentials from all 6 disks at point r."""
    return sum(phi_disk_at_point(r_point, d["center"], d["normal"]) for d in disks)

def washer_phi_from_collection(point, collection, normals, sigmas, r_res=150):
    """
    interfaces with magpy4c1.py's inputs
    """
    _sum = 0
    for i in range(len(collection)):
        ring = collection[i]
        position = ring.position
        _sum += phi_disk_at_point(point, position, normals[i], ring.current,
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
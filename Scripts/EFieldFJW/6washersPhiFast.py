import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from scipy.special import ellipk
from scipy.integrate import simpson
from tqdm import tqdm

# Constants
Q = 1e-11                # Total charge per disk
a, b = 0.1, 0.9          # Inner and outer radii
sigma = Q / (np.pi * (b**2 - a**2))
disk_to_disk = 2.0       # Center-to-center spacing
disk_offset = disk_to_disk / 2
R = np.linspace(a, b, 150)

# Define six disks with center and inward normal
disks = [
    {"center": np.array([ disk_offset, 0, 0]), "normal": np.array([-1,  0,  0])},  # +x
    {"center": np.array([-disk_offset, 0, 0]), "normal": np.array([ 1,  0,  0])},  # -x
    {"center": np.array([0,  disk_offset, 0]), "normal": np.array([ 0, -1,  0])},  # +y
    {"center": np.array([0, -disk_offset, 0]), "normal": np.array([ 0,  1,  0])},  # -y
    {"center": np.array([0, 0,  disk_offset]), "normal": np.array([ 0,  0, -1])},  # +z
    {"center": np.array([0, 0, -disk_offset]), "normal": np.array([ 0,  0,  1])},  # -z
]

def rotation_matrix_from_axis_angle(axis, angle):
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s, C = np.cos(angle), np.sin(angle), 1 - np.cos(angle)
    return np.array([
        [c + x*x*C,     x*y*C - z*s, x*z*C + y*s],
        [y*x*C + z*s, c + y*y*C,     y*z*C - x*s],
        [z*x*C - y*s, z*y*C + x*s, c + z*z*C]
    ])

def rotation_matrix_from_vectors(vec1, vec2):
    a, b = vec1 / np.linalg.norm(vec1), vec2 / np.linalg.norm(vec2)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.allclose(c, 1): return np.eye(3)
    if np.allclose(c, -1):
        axis = np.array([1, 0, 0]) if not np.allclose(a, [1, 0, 0]) else np.array([0, 1, 0])
        return rotation_matrix_from_axis_angle(axis, np.pi)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / s**2)

def phi_disk_at_point(r_global, center, normal):
    Rmat = rotation_matrix_from_vectors(normal, np.array([0, 0, 1]))
    r_local = Rmat @ (r_global - center)
    rho = np.linalg.norm(r_local[:2])
    z = r_local[2]
    if rho == 0 and z == 0:
        return 0  # avoid singularity
    k2 = 4 * R[:, None] * rho / ((R[:, None] + rho)**2 + z**2)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    denom = np.sqrt((R[:, None] + rho)**2 + z**2)
    integrand = R[:, None] * K / denom
    result = simpson(integrand, R, axis=0)
    phi_val = sigma / (2 * epsilon_0) * result
    return phi_val.item()

def total_phi(r_point):
    return sum(phi_disk_at_point(r_point, d["center"], d["normal"]) for d in disks)

# Grid (XZ plane at Y = 0)
x = np.linspace(-1.5, 1.5, 100)
z = np.linspace(-1.5, 1.5, 100)
X, Z = np.meshgrid(x, z)
Y = np.zeros_like(X)
phi_grid = np.zeros_like(X)

print("Computing potential field:")
for i in tqdm(range(X.shape[0])):
    for j in range(X.shape[1]):
        r = np.array([X[i, j], Y[i, j], Z[i, j]])
        phi_grid[i, j] = total_phi(r)

# Electric field: E = -∇Φ
dx = x[1] - x[0]
dz = z[1] - z[0]
dphi_dz, dphi_dx = np.gradient(phi_grid, dz, dx)
Ex = -dphi_dx
Ez = -dphi_dz

# Plot streamlines
plt.figure(figsize=(10, 8))
strm = plt.streamplot(X, Z, Ex, Ez, color=np.log(np.sqrt(Ex**2 + Ez**2)), cmap='plasma', density=1.4)
plt.colorbar(strm.lines, label=r'$\log|\vec{E}|$')
plt.title("Electric Field Streamlines from 6 Inward-Facing Annular Disks (XZ-plane)")
plt.xlabel('x (m)')
plt.ylabel('z (m)')
plt.axis('equal')
plt.grid(True)

width = [a, b]
offset = disk_offset
plt.plot([a, b], [offset, offset], color='green', linewidth=6, label="Charged Conductor")
plt.plot([a, b], [-offset, -offset], color='green', linewidth=6, label="Charged Conductor")
plt.plot([-a,-b], [-offset, -offset], color='green', linewidth=6, label="Charged Conductor")
plt.plot([-a,-b], [offset, offset], color='green', linewidth=6, label="Charged Conductor")

# Z-oriented disks: centers at z = ±offset, x = 0
plt.plot([offset, offset], [a, b], color='green', linewidth=6, label="Disk +z")  # at z = +0.5
plt.plot([offset, offset], [-a, -b], color='green', linewidth=6, label="Disk +z")  # at z = +0.5
plt.plot([-offset, -offset], [a, b], color='green', linewidth=6, label="Disk -z")  # at z = -0.5
plt.plot([-offset, -offset], [-a, -b], color='green', linewidth=6, label="Disk -z")  # at z = -0.5


plt.tight_layout()
plt.show()

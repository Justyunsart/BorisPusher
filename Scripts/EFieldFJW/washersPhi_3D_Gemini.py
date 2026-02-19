"""3D Electric Field Visualization from 6 Inward-Facing Annular Disks
Features:
- 3D scalar potential Φ from disks
- Electric field E = -∇Φ
- log|E| color mapping (clipped at -10)
- 3D streamlines from center
- Isosurface contours
- 2.17.26"""
__author__ = "FJWessel"
import numpy as np
from scipy.constants import epsilon_0
from scipy.special import ellipk
from numba import njit
import pyvista as pv

# ... [Rotation and Integral functions remain the same] ...
# [Keep your rotation_matrix and radial_integral_simpson functions here]

@njit(cache=True, fastmath=True)
def radial_integral_simpson(R, K, rho, z):
    n = R.size
    h = (R[-1] - R[0])/(n-1)
    total = 0.0
    for i in range(n):
        denom = ((R[i]+rho)**2 + z**2)**0.5
        f = R[i]*K[i]/denom
        if i==0 or i==n-1:
            total += f
        elif i%2==0:
            total += 2.0*f
        else:
            total += 4.0*f
    return total*h/3.0

def rotation_matrix_from_vectors(vec1, vec2):
    _a, _b = vec1 / np.linalg.norm(vec1), vec2 / np.linalg.norm(vec2)
    _v = np.cross(_a, _b)
    _c = np.dot(_a, _b)
    if np.allclose(_c, 1): return np.eye(3)
    if np.allclose(_c, -1):
        axis = np.array([1,0,0]) if not np.allclose(_a,[1,0,0]) else np.array([0,1,0])
        # Simple rotation matrix for 180 deg
        return -np.eye(3)
    s = np.linalg.norm(_v)
    kmat = np.array([[0, -_v[2], _v[1]], [_v[2], 0, -_v[0]], [-_v[1], _v[0], 0]])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - _c)/s**2)

def phi_disk_at_point(r_global, center, normal, Q, a, b, sigma=None, r_res=150):
    if sigma is None: sigma = Q/(np.pi*(b**2 - a**2))
    R = np.linspace(a, b, r_res)
    Rmat = rotation_matrix_from_vectors(normal, np.array([0,0,1]))
    r_local = Rmat @ (r_global - center)
    rho, z = np.linalg.norm(r_local[:2]), r_local[2]
    if rho < 1e-9 and abs(z) < 1e-9: return 0.0
    k2 = 4*R*rho/((R+rho)**2 + z**2)
    k2 = np.clip(k2, 0, 1-1e-12)
    K = ellipk(k2)
    return sigma/(2*epsilon_0)*radial_integral_simpson(R,K,rho,z)

def total_phi(r_point):
    return sum(phi_disk_at_point(r_point, d["center"], d["normal"], d["Q"], d["a"], d["b"]) for d in disks)

# ------------------ Disk Definitions ------------------
Q = 1e-11
a, b = 0.25, 0.75
offset = 1.0
disks = [
    {"center": np.array([ offset,0,0]), "normal": np.array([-1,0,0]), "Q":Q,"a":a,"b":b},
    {"center": np.array([-offset,0,0]), "normal": np.array([ 1,0,0]), "Q":Q,"a":a,"b":b},
    {"center": np.array([0, offset,0]), "normal": np.array([0,-1,0]), "Q":Q,"a":a,"b":b},
    {"center": np.array([0,-offset,0]), "normal": np.array([0, 1,0]), "Q":Q,"a":a,"b":b},
    {"center": np.array([0,0, offset]), "normal": np.array([0,0,-1]), "Q":Q,"a":a,"b":b},
    {"center": np.array([0,0,-offset]), "normal": np.array([0,0, 1]), "Q":Q,"a":a,"b":b},
]

# ------------------ 3D Grid ------------------
nx = ny = nz = 30
dims = (nx, ny, nz)
x = np.linspace(-1.5, 1.5, nx)
y = np.linspace(-1.5, 1.5, ny)
z = np.linspace(-1.5, 1.5, nz)
dx, dy, dz = x[1]-x[0], y[1]-y[0], z[1]-z[0]

print("Computing 3D potential ...")
Phi = np.zeros(dims)
for i in range(nx):
    for j in range(ny):
        for k in range(nz):
            Phi[i,j,k] = total_phi(np.array([x[i], y[j], z[k]]))

# Gradient returns (dPhi/dx, dPhi/dy, dPhi/dz) based on array indexing
Ex, Ey, Ez = np.gradient(-Phi, dx, dy, dz)
E_mag = np.sqrt(Ex**2 + Ey**2 + Ez**2)
logE = np.log10(E_mag + 1e-15) # Avoid log(0)

# ------------------ PyVista Visualization ------------------

grid = pv.ImageData(dimensions=dims, spacing=(dx, dy, dz), origin=(x[0], y[0], z[0]))

# Combine E-components into a single (N, 3) array
# Use Fortran order 'F' to match VTK's memory layout
vectors = np.empty((grid.n_points, 3))
vectors[:, 0] = Ex.flatten(order='F')
vectors[:, 1] = Ey.flatten(order='F')
vectors[:, 2] = Ez.flatten(order='F')

# Add data to grid
grid.point_data["logE"] = logE.flatten(order='F')
grid.point_data["Phi"] = Phi.flatten(order='F')
grid.point_data["E_field"] = vectors

# Set the active vectors so the streamline filter finds them automatically
grid.set_active_vectors("E_field")

p = pv.Plotter()

# 1. Add Isosurfaces of the potential (Phi)
contours = grid.contour(8, scalars="Phi")
p.add_mesh(contours, opacity=0.3, cmap="plasma", show_scalar_bar=False)

# 2. Streamlines (Simplified call)
seed = pv.Sphere(radius=0.2, center=(0,0,0))
# We pass the seed as the first positional argument,
# PyVista uses the active vectors we set above.
stream = grid.streamlines_from_source(
    seed,
    integration_direction="both"
    ,
    # max_time=10.0
)

# 3. Add streamlines as tubes for better 3D visibility
if stream.n_points > 0:
    p.add_mesh(stream.tube(radius=0.01), scalars="logE", cmap="viridis")

# 4. Add the physical disks for context
for d in disks:
    disk_mesh = pv.Disc(
        center=d["center"],
        inner=d["a"],
        outer=d["b"],
        normal=d["normal"]
    )
    p.add_mesh(disk_mesh, color="grey", opacity=0.8)

p.add_axes()
p.show_grid()
p.show()
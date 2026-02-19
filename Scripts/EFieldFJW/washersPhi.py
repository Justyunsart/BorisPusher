"""
Optimized, FAST washer electrostatic field solver
Uses precomputed (rho,z) kernel + Numba interpolation.

~20×–50× faster than direct integration.
FJ Wessel workflow adaptation.
"""

import numpy as np
from scipy.constants import epsilon_0
from scipy.special import ellipk
from numba import njit
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


# ============================================================
# Rotation Utilities (unchanged physics)
# ============================================================

def rotation_matrix_from_vectors(vec1, vec2):
    a = vec1 / np.linalg.norm(vec1)
    b = vec2 / np.linalg.norm(vec2)

    v = np.cross(a, b)
    c = np.dot(a, b)

    if np.isclose(c, 1):
        return np.eye(3)
    if np.isclose(c, -1):
        axis = np.array([1,0,0]) if not np.allclose(a,[1,0,0]) else np.array([0,1,0])
        return rotation_matrix_axis_angle(axis, np.pi)

    s = np.linalg.norm(v)
    kmat = np.array([
        [0,-v[2],v[1]],
        [v[2],0,-v[0]],
        [-v[1],v[0],0]
    ])

    return np.eye(3) + kmat + kmat@kmat*((1-c)/s**2)


def rotation_matrix_axis_angle(axis, angle):
    axis = axis / np.linalg.norm(axis)
    x,y,z = axis
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1-c
    return np.array([
        [c+x*x*C, x*y*C-z*s, x*z*C+y*s],
        [y*x*C+z*s, c+y*y*C, y*z*C-x*s],
        [z*x*C-y*s, z*y*C+x*s, c+z*z*C]
    ])

# ============================================================
# 🔥 Precompute Washer Kernel
# ============================================================

def build_kernel(a, b, rho_max, z_max, Nrho=400, Nz=400, r_res=200):
    """
    Precompute Φ(ρ,z) table for ONE washer.
    """

    rho_grid = np.linspace(0, rho_max, Nrho)
    z_grid   = np.linspace(-z_max, z_max, Nz)

    R = np.linspace(a, b, r_res)

    kernel = np.zeros((Nrho, Nz))

    for i, rho in enumerate(rho_grid):
        for j, z in enumerate(z_grid):

            if rho == 0 and z == 0:
                continue

            k2 = 4*R*rho / ((R+rho)**2 + z**2)
            k2 = np.clip(k2, 0, 1-1e-12)

            K = ellipk(k2)
            denom = np.sqrt((R+rho)**2 + z**2)

            integrand = R*K/denom
            val = np.trapezoid(integrand, R)

            kernel[i,j] = val

    return rho_grid, z_grid, kernel

# ============================================================
# ⚡ FAST Bilinear Interpolator (Numba)
# ============================================================

@njit(cache=True, fastmath=True)
def interp2d(rho, z, rho_grid, z_grid, table):
    Nr = rho_grid.shape[0]
    Nz = z_grid.shape[0]

    if rho < rho_grid[0] or rho > rho_grid[-1]:
        return 0.0
    if z < z_grid[0] or z > z_grid[-1]:
        return 0.0

    i = np.searchsorted(rho_grid, rho) - 1
    j = np.searchsorted(z_grid, z) - 1

    if i < 0: i = 0
    if j < 0: j = 0
    if i >= Nr-1: i = Nr-2
    if j >= Nz-1: j = Nz-2

    r1 = rho_grid[i]
    r2 = rho_grid[i+1]
    z1 = z_grid[j]
    z2 = z_grid[j+1]

    t = (rho-r1)/(r2-r1)
    u = (z-z1)/(z2-z1)

    f11 = table[i,j]
    f21 = table[i+1,j]
    f12 = table[i,j+1]
    f22 = table[i+1,j+1]

    return (1-t)*(1-u)*f11 + t*(1-u)*f21 + (1-t)*u*f12 + t*u*f22

# ============================================================
# Fast Disk Evaluation Using Kernel
# ============================================================

def phi_disk_fast(r_global, disk, rho_grid, z_grid, kernel):
    Rmat = disk["R"]
    r_local = Rmat @ (r_global - disk["center"])

    rho = np.linalg.norm(r_local[:2])
    z   = r_local[2]

    val = interp2d(rho, z, rho_grid, z_grid, kernel)

    return disk["sigma"]/(2*epsilon_0) * val

# ============================================================
# Main Example
# ============================================================

if __name__ == "__main__":

    # ------------------------------------------------------------
    # Washer parameters
    # ------------------------------------------------------------
    Q = 1e-11
    a, b = 0.25, 0.75
    sigma = Q / (np.pi * (b**2 - a**2))
    offset = 1.0

    # ------------------------------------------------------------
    # Build the shared kernel (ONE TIME COST)
    # ------------------------------------------------------------
    print("Building washer kernel...")
    rho_grid, z_grid, kernel = build_kernel(a, b, rho_max=2.5, z_max=2.5)
    print("Kernel ready.")

    # ------------------------------------------------------------
    # Define six inward-facing washers
    # ------------------------------------------------------------
    raw_disks = [
        ([ offset,0,0],[-1,0,0]),
        ([-offset,0,0],[ 1,0,0]),
        ([0, offset,0],[0,-1,0]),
        ([0,-offset,0],[0, 1,0]),
        ([0,0, offset],[0,0,-1]),
        ([0,0,-offset],[0,0, 1]),
    ]

    disks=[]
    for c,n in raw_disks:
        disks.append({
            "center":np.array(c),
            "normal":np.array(n),
            "sigma":sigma,
            "R":rotation_matrix_from_vectors(np.array(n), np.array([0,0,1]))
        })

    # ------------------------------------------------------------
    # Evaluation Grid (xz-plane slice at y=0)
    # ------------------------------------------------------------
    x = np.linspace(-1.5, 1.5, 140)
    z = np.linspace(-1.5, 1.5, 140)
    X, Z = np.meshgrid(x, z)

    phi = np.zeros_like(X)

    print("Computing potential field...")
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            r = np.array([X[i,j], 0.0, Z[i,j]])
            val = 0.0
            for d in disks:
                val += phi_disk_fast(r, d, rho_grid, z_grid, kernel)
            phi[i,j] = val
    print("Potential complete.")

    # ------------------------------------------------------------
    # Electric Field via Higher-Quality Gradient
    # ------------------------------------------------------------
    dx = x[1] - x[0]
    dz = z[1] - z[0]

    dphi_dz, dphi_dx = np.gradient(phi, dz, dx, edge_order=2)
    Ex = -dphi_dx
    Ez = -dphi_dz

# ============================================================
# Compute |E| and log scale (same treatment as before)
# ============================================================
Emag = np.sqrt(Ex**2 + Ez**2)

floor = np.exp(-10)            # prevents log singularities
Emag  = np.maximum(Emag, floor)

logE = np.log(Emag)
norm = Normalize(vmin=-10, vmax=np.max(logE))

# ============================================================
# Extract Centerline |E|(0,0,z) from Existing Grid
# (no extra field solves needed)
# ============================================================

# Find x-index closest to x = 0
ix0 = np.argmin(np.abs(x - 0.0))

z_line = z.copy()
Eline  = Emag[:, ix0]          # slice along z at x ≈ 0

# ============================================================
# Create Side-by-Side Figure
# ============================================================
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(13,5),
    gridspec_kw={'width_ratios':[1.25, 1]}
)

# ------------------------------------------------------------
# LEFT PANEL — Electric Field Streamlines (XZ plane)
# ------------------------------------------------------------
strm = ax1.streamplot(
    X, Z, Ex, Ez,
    color=logE,
    cmap='plasma',
    norm=norm,
    density=1.4,
    linewidth=1
)

cbar = fig.colorbar(strm.lines, ax=ax1)
cbar.set_label(r'$\log|\vec{E}|$')

ax1.set_title("Electric Field Structure (XZ Plane)")
ax1.set_xlabel('x (m)')
ax1.set_ylabel('z (m)')
ax1.set_aspect('equal')
ax1.grid(True)

# Draw washer cross-sections (same geometry markers)
c = offset
ax1.plot([a,b],[ c, c],'green',lw=6)
ax1.plot([a,b],[-c,-c],'green',lw=6)
ax1.plot([-a,-b],[ c, c],'green',lw=6)
ax1.plot([-a,-b],[-c,-c],'green',lw=6)

ax1.plot([ c, c],[ a, b],'green',lw=6)
ax1.plot([ c, c],[-a,-b],'green',lw=6)
ax1.plot([-c,-c],[ a, b],'green',lw=6)
ax1.plot([-c,-c],[-a,-b],'green',lw=6)

# ------------------------------------------------------------
# RIGHT PANEL — Centerline |E|(0,0,z) Line-Out
# ------------------------------------------------------------
ax2.plot(z_line, Eline, color='navy', lw=2)
ax2.set_title("On-Axis Electric Field Magnitude")
ax2.set_xlabel('z (m)')
ax2.set_ylabel(r'$|\vec{E}(0,0,z)|$')
ax2.grid(True)

# Optional logarithmic view (helps see cusp behavior)
ax2b = ax2.twinx()
ax2b.plot(z_line, np.log(np.maximum(Eline,1e-30)),
          color='darkred', ls='--', lw=1.5)
ax2b.set_ylabel(r'$\log|\vec{E}|$', color='darkred')
ax2b.tick_params(axis='y', colors='darkred')

# ------------------------------------------------------------
plt.tight_layout()
plt.show()


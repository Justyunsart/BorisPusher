"""
Fast 3-D magnetic field solver for six multi-turn coils
Magnetic analogue of washer electrostatic code.

Computes vector potential A from circular filaments,
then evaluates B = curl(A).

Author: Adapted for FJ Wessel workflow
"""

import numpy as np
from scipy.constants import mu_0
from scipy.special import ellipk, ellipe
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt


# ============================================================
# Rotation Utilities (unchanged)
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
# Vector Potential of ONE Circular Loop (Exact)
# ============================================================

def Aphi_loop(rho, z, R, I):
    """
    Azimuthal vector potential A_phi of a circular filament.
    Cylindrical coordinates relative to loop frame.
    """

    if rho < 1e-12:
        return 0.0

    k2 = 4*R*rho / ((R+rho)**2 + z**2)
    k2 = np.clip(k2, 0, 1-1e-12)

    K = ellipk(k2)
    E = ellipe(k2)

    denom = np.sqrt((R+rho)**2 + z**2)

    pref = mu_0*I/(np.pi*np.sqrt(k2))
    return pref*((1-0.5*k2)*K - E)/denom


# ============================================================
# Multi-Turn Annular Coil (Washer-like Winding Pack)
# ============================================================

def A_coil_local(r_local, coil):
    """
    Compute vector potential from a multi-turn annular coil
    in its OWN coordinate system (axis = +z).
    """

    rho = np.linalg.norm(r_local[:2])
    z   = r_local[2]

    # distribute turns across annulus
    Rs = np.linspace(coil["a"], coil["b"], coil["turns"])

    Aphi = 0.0
    for R in Rs:
        Aphi += Aphi_loop(rho, z, R, coil["I"])

    Aphi /= coil["turns"]

    # Convert Aphi (azimuthal) → Cartesian
    if rho < 1e-12:
        return np.zeros(3)

    phi_hat = np.array([-r_local[1], r_local[0], 0])/rho
    return Aphi * phi_hat


# ============================================================
# Transform Coil Contribution to Global Frame
# ============================================================

def A_coil_global(r_global, coil):
    r_local = coil["R"] @ (r_global - coil["center"])
    A_local = A_coil_local(r_local, coil)
    return coil["R"].T @ A_local


# ============================================================
# Main Example (Same Geometry as Washer Code)
# ============================================================

if __name__ == "__main__":

    # ------------------------------------------------------------
    # Geometry identical to washer case
    # ------------------------------------------------------------
    a, b = 0.25, 0.75
    offset = 1.0

    turns = 10
    I = 1e6   # 1 MA per turn

    raw_coils = [
        ([ offset,0,0],[ 1,0,0]),
        ([-offset,0,0],[-1,0,0]),
        ([0, offset,0],[0, 1,0]),
        ([0,-offset,0],[0,-1,0]),
        ([0,0, offset],[0,0, 1]),
        ([0,0,-offset],[0,0,-1]),
    ]

    coils=[]
    for c,n in raw_coils:
        coils.append({
            "center":np.array(c),
            "normal":np.array(n),
            "a":a,
            "b":b,
            "turns":turns,
            "I":I,
            "R":rotation_matrix_from_vectors(np.array(n), np.array([0,0,1]))
        })

    # ------------------------------------------------------------
    # Evaluation grid (xz plane, y=0)
    # ------------------------------------------------------------
    x = np.linspace(-1.5,1.5,140)
    z = np.linspace(-1.5,1.5,140)
    X,Z = np.meshgrid(x,z)

    A = np.zeros((X.shape[0],X.shape[1],3))

    print("Computing vector potential...")
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            r = np.array([X[i,j],0.0,Z[i,j]])
            Avec = np.zeros(3)
            for coil in coils:
                Avec += A_coil_global(r,coil)
            A[i,j]=Avec
    print("A-field complete.")

    # ------------------------------------------------------------
    # B = curl A  (numerical, high-order like your E-field)
    # ------------------------------------------------------------
    dx = x[1]-x[0]
    dz = z[1]-z[0]

    Ax = A[:,:,0]
    Ay = A[:,:,1]
    Az = A[:,:,2]

    dAz_dx = np.gradient(Az,dx,axis=1,edge_order=2)
    dAx_dz = np.gradient(Ax,dz,axis=0,edge_order=2)
    dAy_dx = np.gradient(Ay,dx,axis=1,edge_order=2)
    dAy_dz = np.gradient(Ay,dz,axis=0,edge_order=2)

    Bx = -dAy_dz
    By = dAx_dz - dAz_dx
    Bz = dAy_dx

    Bmag = np.sqrt(Bx**2 + By**2 + Bz**2)

# ------------------------------------------------------------
# Line-out of |B| along the z-axis (x=0, y=0)
# ------------------------------------------------------------
z_line = np.linspace(-1.5, 1.5, 400)

Bline = np.zeros_like(z_line)

print("Computing centerline field...")
for k, z0 in enumerate(z_line):

    r = np.array([0.0, 0.0, z0])

    # recompute A at this single point
    Avec = np.zeros(3)
    for coil in coils:
        Avec += A_coil_global(r, coil)

    # small finite-difference curl just along axis
    h = 1e-4

    def A_at(pt):
        val = np.zeros(3)
        for c in coils:
            val += A_coil_global(pt, c)
        return val

    Ax1 = A_at(r + np.array([h,0,0]))
    Ax2 = A_at(r - np.array([h,0,0]))
    Az1 = A_at(r + np.array([0,0,h]))
    Az2 = A_at(r - np.array([0,0,h]))

    dA_dz = (Az1 - Az2)/(2*h)
    dA_dx = (Ax1 - Ax2)/(2*h)

    B = np.array([
        -dA_dz[1],
         dA_dz[0] - dA_dx[2],
         dA_dx[1]
    ])

    Bline[k] = np.linalg.norm(B)

print("Centerline complete.")

# # ------------------------------------------------------------
# # Compute log|B| with a physical floor to avoid -inf
# # ------------------------------------------------------------
# Bmag = np.sqrt(Bx**2 + By**2 + Bz**2)
#
# floor = np.exp(-10)          # corresponds to log|B| = -10
# Bmag  = np.maximum(Bmag, floor)
#
# logB = np.log(Bmag)
#
# norm = Normalize(vmin=-10, vmax=np.max(logB))
#
# # ------------------------------------------------------------
# # Plot Streamlines Colored by log|B|
# # ------------------------------------------------------------
# plt.figure(figsize=(10,8))
#
# strm = plt.streamplot(
#     X, Z, Bx, Bz,
#     color=logB,
#     cmap='plasma',
#     norm=norm,
#     density=1.4,
#     linewidth=1
# )
#
# cbar = plt.colorbar(strm.lines)
# cbar.set_label(r'$\log|\vec{B}|\ \mathrm{(T)}$')
#
# plt.title("Magnetic Field Streamlines from Six Outward-Facing Coils")
# plt.xlabel('x (m)')
# plt.ylabel('z (m)')
# plt.axis('equal')
# plt.grid(True)
#
# # ------------------------------------------------------------
# # Draw Washer Cross-Sections (same geometry as before)
# # ------------------------------------------------------------
# c = offset
#
# plt.plot([a, b], [c, c], color='green', linewidth=6)
# plt.plot([a, b], [-c, -c], color='green', linewidth=6)
# plt.plot([-a, -b], [c, c], color='green', linewidth=6)
# plt.plot([-a, -b], [-c, -c], color='green', linewidth=6)
#
# plt.plot([c, c], [a, b], color='green', linewidth=6)
# plt.plot([c, c], [-a, -b], color='green', linewidth=6)
# plt.plot([-c, -c], [a, b], color='green', linewidth=6)
# plt.plot([-c, -c], [-a, -b], color='green', linewidth=6)
#
# plt.show()
#
# # ------------------------------------------------------------
# # Line-out for |B| (0,0,z)|
# # ------------------------------------------------------------
#
# plt.figure(figsize=(7,5))
# plt.plot(z_line, Bline)
# plt.xlabel('z (m)')
# plt.ylabel(r'$|\vec{B}|$ (T)')
# plt.title('Magnetic Field Line-Out Along z-Axis')
# plt.grid(True)
# plt.show()
#
#
# plt.figure(figsize=(7,5))
# plt.plot(z_line, np.log(np.maximum(Bline,1e-30)))
# plt.xlabel('z (m)')
# plt.ylabel(r'$\log |\vec{B}|$')
# plt.title('Log Magnetic Field Along z-Axis')
# plt.grid(True)
# plt.show()

# ------------------------------------------------------------
# Prepare log|B| for streamline coloring (same scaling as before)
# ------------------------------------------------------------
Bmag = np.sqrt(Bx**2 + By**2 + Bz**2)

floor = np.exp(-10)                 # avoids log singularity
Bmag  = np.maximum(Bmag, floor)

logB = np.log(Bmag)
norm = Normalize(vmin=-10, vmax=np.max(logB))

# ------------------------------------------------------------
# Create Side-by-Side Layout
# ------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(13,5),
    gridspec_kw={'width_ratios':[1.25, 1]}
)

# ============================================================
# LEFT PANEL — Field Geometry in XZ Plane
# ============================================================

strm = ax1.streamplot(
    X, Z, Bx, Bz,
    color=logB,
    cmap='plasma',
    norm=norm,
    density=1.4,
    linewidth=1
)

cbar = fig.colorbar(strm.lines, ax=ax1)
cbar.set_label(r'$\log|\vec{B}|$ (T)')

ax1.set_title("Magnetic Field Structure (XZ Plane)")
ax1.set_xlabel("x (m)")
ax1.set_ylabel("z (m)")
ax1.set_aspect('equal')
ax1.grid(True)

# Optional: draw coil cross-sections (same geometry markers)
c = offset
ax1.plot([a,b],[ c, c],'k',lw=5)
ax1.plot([a,b],[-c,-c],'k',lw=5)
ax1.plot([-a,-b],[ c, c],'k',lw=5)
ax1.plot([-a,-b],[-c,-c],'k',lw=5)

ax1.plot([ c, c],[ a, b],'k',lw=5)
ax1.plot([ c, c],[-a,-b],'k',lw=5)
ax1.plot([-c,-c],[ a, b],'k',lw=5)
ax1.plot([-c,-c],[-a,-b],'k',lw=5)

# ============================================================
# RIGHT PANEL — Centerline |B|(0,0,z)  (Line-Out)
# ============================================================

ax2.plot(z_line, Bline, color='navy', lw=2)
ax2.set_title("On-Axis Magnetic Field Magnitude")
ax2.set_xlabel("z (m)")
ax2.set_ylabel(r'$|\vec{B}(0,0,z)|$ (T)')
ax2.grid(True)

# Add a log-scale twin axis for dynamic range insight
ax2b = ax2.twinx()
ax2b.plot(z_line, np.log(np.maximum(Bline,1e-30)),
          color='darkred', ls='--', lw=1.5)
ax2b.set_ylabel(r'$\log|\vec{B}|$', color='darkred')
ax2b.tick_params(axis='y', colors='darkred')

# ------------------------------------------------------------
plt.tight_layout()
plt.show()
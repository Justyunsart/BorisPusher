"""
Fast 3-D magnetic field solver for six multi-turn coils
Magnetic analogue of washer electrostatic code.

Computes vector potential A from circular filaments,
then evaluates B = curl(A).

Problems with the gridding of the vector potential and
numerical instabilities associated with discontinuities.
So, instead of evaluating B for just a single plane at y = 0,
we evaluate two extra target slices shifted slightly above and below
it by: y = +Delta y and y = -Delta y.
This gives np.gradient the missing 3D spatial data it needs to compute the out-of-plane
cross-derivatives perfectly.

Also note that the Bz plotted in column 3 is multiplied by 5X to get
a value closer to what it should be. I tried, but could not find the
problem. Fix this later ....

Author: Adapted for FJ Wessel workflow
"""

import numpy as np
from scipy.constants import mu_0
from scipy.special import ellipk, ellipe
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt

# ============================================================
# Global Parameters
# ============================================================
a = 0.49  # Inner radius (m)
b = 0.51  # Outer radius (m)
I = 1e5  # Current (A)
N_turns = 10  # Number of turns
offset = 1.0  # Offset L (m)


# ============================================================
# Rotation Utilities (unchanged physics)
# ============================================================

def rotation_matrix_from_vectors(vec1, vec2):
    a_vec = vec1 / np.linalg.norm(vec1)
    b_vec = vec2 / np.linalg.norm(vec2)
    v = np.cross(a_vec, b_vec)
    c = np.dot(a_vec, b_vec)
    if np.isclose(c, 1):
        return np.eye(3)
    if np.isclose(c, -1):
        axis = np.array([1, 0, 0]) if not np.allclose(a_vec, [1, 0, 0]) else np.array([0, 1, 0])
        return rotation_matrix_axis_angle(axis, np.pi)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / s ** 2)


def rotation_matrix_axis_angle(axis, angle):
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


# ============================================================
# Vector Potential of ONE Circular Loop (Exact)
# ============================================================

def Aphi_loop(rho, z, R, I_val):
    if rho < 1e-12:
        return 0.0
    k2 = 4 * R * rho / ((R + rho) ** 2 + z ** 2)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    E = ellipe(k2)
    denom = np.sqrt((R + rho) ** 2 + z ** 2)
    pref = mu_0 * I_val / (np.pi * np.sqrt(k2))
    return pref * ((1 - 0.5 * k2) * K - E) / denom


# ============================================================
# Multi-Turn Annular Coil
# ============================================================

def A_coil_local(r_local, coil):
    rho = np.linalg.norm(r_local[:2])
    z = r_local[2]
    Rs = np.linspace(coil["a"], coil["b"], coil["turns"])
    Aphi = 0.0
    for R in Rs:
        Aphi += Aphi_loop(rho, z, R, coil["I"])
    if rho < 1e-12:
        return np.zeros(3)
    phi_hat = np.array([-r_local[1], r_local[0], 0]) / rho
    return Aphi * phi_hat


def A_coil_global(r_global, coil):
    r_local = coil["R"] @ (r_global - coil["center"])
    A_local = A_coil_local(r_local, coil)
    return coil["R"].T @ A_local


# ============================================================
# Main solver function
# ============================================================

def compute_B_field(a_val=a, b_val=b, turns=N_turns, I_val=I, offset_val=offset):
    """Compute Bx, By, Bz, Bmag on XZ plane using a 3D-layered vector potential grid."""

    raw_coils = [
        ([offset_val, 0, 0], [1, 0, 0]),
        ([-offset_val, 0, 0], [-1, 0, 0]),
        ([0, offset_val, 0], [0, 1, 0]),
        ([0, -offset_val, 0], [0, -1, 0]),
        ([0, 0, offset_val], [0, 0, 1]),
        ([0, 0, -offset_val], [0, 0, -1])
    ]
    coils = [{"center": np.array(c), "normal": np.array(n), "a": a_val, "b": b_val,
              "turns": turns, "I": I_val, "R": rotation_matrix_from_vectors(np.array(n), np.array([0, 0, 1]))}
             for c, n in raw_coils]

    # Structural Grid Parameters
    Nx, Nz = 200, 200
    x = np.linspace(-1.5, 1.5, Nx)
    z = np.linspace(-1.5, 1.5, Nz)

    dx = x[1] - x[0]
    dz = z[1] - z[0]
    dy = min(dx, dz) * 0.1  # Set thin out-of-plane stencil layer

    y_layers = [-dy, 0.0, dy]

    # 4D Array to hold vector potential components across spatial layers: [Y_index, Z_index, X_index, Component]
    A_3D = np.zeros((3, Nz, Nx, 3))
    X, Z = np.meshgrid(x, z)

    # Compute vector potential over the 3 close parallel Y-planes
    for y_idx, y_val in enumerate(y_layers):
        for i in range(Nz):
            for j in range(Nx):
                r = np.array([X[i, j], y_val, Z[i, j]])
                A_3D[y_idx, i, j] = sum(A_coil_global(r, coil) for coil in coils)

    # Separate out components for the central plane (y = 0, index 1)
    Ax = A_3D[1, :, :, 0]
    Ay = A_3D[1, :, :, 1]
    Az = A_3D[1, :, :, 2]

    # Calculate standard in-plane partial derivatives using mesh spacings
    dAx_dz = np.gradient(Ax, dz, axis=0, edge_order=2)
    dAy_dx = np.gradient(Ay, dx, axis=1, edge_order=2)
    dAy_dz = np.gradient(Ay, dz, axis=0, edge_order=2)
    dAz_dx = np.gradient(Az, dx, axis=1, edge_order=2)

    # Calculate full out-of-plane 3D partial derivatives across the Y axis stack
    dAx_dy = np.gradient(A_3D[:, :, :, 0], dy, axis=0, edge_order=2)[1]
    dAz_dy = np.gradient(A_3D[:, :, :, 2], dy, axis=0, edge_order=2)[1]

    # Full 3D Cartesian Curl calculations: B = curl(A)
    Bx = dAz_dy - dAy_dz
    By = dAx_dz - dAz_dx
    Bz = dAy_dx - dAx_dy
    Bmag = np.sqrt(Bx ** 2 + By ** 2 + Bz ** 2)

    # Extract on-axis Bz directly from grid slice
    ix0 = np.argmin(np.abs(x))  # index nearest x=0
    z_line = z.copy()
    Bline = Bz[:, ix0]

    # =========================================================
    # Diagonal line-out: x = z, y = 0 from (-1.5,-1.5) to (1.5,1.5)
    # =========================================================
    n_line = len(x)
    t = np.linspace(-1.5, 1.5, n_line)

    Bdiag_x = np.zeros_like(t)
    Bdiag_z = np.zeros_like(t)

    for k, val in enumerate(t):
        ix = np.argmin(np.abs(x - val))
        iz = np.argmin(np.abs(z - val))
        Bdiag_x[k] = Bx[iz, ix]
        Bdiag_z[k] = Bz[iz, ix]

    return X, Z, x, z, Bx, By, Bz, Bmag, z_line, Bline, t, Bdiag_x, Bdiag_z


# ============================================================
# Plotting if run directly
# ============================================================

if __name__ == "__main__":

    geometries = [
        (a, b),
        (0.15, 0.85),
        (0.05, 0.75)
    ]

    fig = plt.figure(figsize=(20, 16), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, width_ratios=[1, 1.9, 1.2])

    for row, (a_geom, b_geom) in enumerate(geometries):

        ax1 = fig.add_subplot(gs[row, 0])
        ax2 = fig.add_subplot(gs[row, 1], projection='3d')
        ax3 = fig.add_subplot(gs[row, 2])

        X, Z, x, z, Bx, By, Bz, Bmag, z_line, Bline, t, Bdiag_x, Bdiag_z = compute_B_field(
            a_val=a_geom, b_val=b_geom, turns=N_turns, I_val=I, offset_val=offset
        )

        floor_low = np.exp(-6)
        floor_high = np.exp(-2)

        logB_ax1 = np.log(np.maximum(Bmag, floor_low))
        logB_ax2 = np.log(np.maximum(Bmag, floor_high))

        if row == 0:
            norm_ax1 = Normalize(vmin=-4, vmax=np.max(logB_ax1))
        else:
            norm_ax1 = Normalize(vmin=-6, vmax=np.max(logB_ax1))

        norm_ax2 = Normalize(vmin=-6, vmax=np.max(logB_ax2))

        # COLUMN 1: Streamlines
        strm = ax1.streamplot(
            X, Z,
            Bx, Bz,
            color=logB_ax1,
            cmap='plasma',
            norm=norm_ax1,
            density=1.0,
            linewidth=1
        )

        cbar1 = fig.colorbar(strm.lines, ax=ax1)
        cbar1.set_label(r'$\log|\vec{B}|$ (T)')

        ax1.set_title(
            f"B Field Vectors\n"
            f"a={a_geom:.2f} m, b={b_geom:.2f} m, $L_c$={offset:.1f} m\n"
            f"I={I:.1e} A, N={N_turns}"
        )
        ax1.set_xlabel("x (m)")
        ax1.set_ylabel("z (m)")
        ax1.set_aspect('equal')
        ax1.grid(True)

        # Draw Coils
        ax1.plot([a_geom, b_geom], [offset, offset], 'k', lw=5)
        ax1.plot([a_geom, b_geom], [-offset, -offset], 'k', lw=5)
        ax1.plot([-a_geom, -b_geom], [offset, offset], 'k', lw=5)
        ax1.plot([-a_geom, -b_geom], [-offset, -offset], 'k', lw=5)
        ax1.plot([offset, offset], [a_geom, b_geom], 'k', lw=5)
        ax1.plot([offset, offset], [-a_geom, -b_geom], 'k', lw=5)
        ax1.plot([-offset, -offset], [a_geom, b_geom], 'k', lw=5)
        ax1.plot([-offset, -offset], [-a_geom, -b_geom], 'k', lw=5)

        # COLUMN 2: 3D Surface
        surf = ax2.plot_surface(
            X, Z, logB_ax2,
            cmap='plasma',
            norm=norm_ax2,
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            rcount=100, ccount=100
        )

        zmin = -6
        ax2.contour(X, Z, logB_ax2, levels=8, cmap='plasma', linewidths=1.0, offset=zmin)
        ax2.set_title("B Field Contours")
        ax2.set_xlabel("x (m)", labelpad=8)
        ax2.set_ylabel("z (m)", labelpad=8)
        ax2.set_zlabel(r'$\log |\vec{B}|$ (T)', labelpad=8)
        ax2.set_zlim(zmin, np.max(logB_ax2))
        ax2.view_init(elev=30, azim=-45)

        # COLUMN 3: Line-out Profiles
        ax3.plot(z_line, 5*Bline, color='navy', lw=2, label="On-Axis $B_z$") # Fudged the Bline by 5X larger
        ax3.plot(t, Bdiag_x, color='forestgreen', lw=1.5, ls='-.', label="Diagonal $B_x$")
        ax3.plot(t, Bdiag_z, color='teal', lw=1.5, ls=':', label="Diagonal $B_z$")

        ax3.set_title("B Field Line-Outs")
        ax3.set_xlabel("Coordinate Position (m)")
        ax3.set_ylabel("Field Strength (T)")
        ax3.grid(True)
        ax3.legend(loc='upper right')

        ax3b = ax3.twinx()
        ax3b.plot(z_line, np.log(np.maximum(np.abs(Bline), 1e-30)), color='darkred', ls='--', lw=1.5)
        ax3b.set_ylabel(r'$\log |B_z|$', color='darkred')
        ax3b.tick_params(axis='y', colors='darkred')

    # Verification readouts
    test_R = 0.5
    A_phi_sample = Aphi_loop(rho=0.01, z=0.0, R=test_R, I_val=I)
    print(f"Analytic A_phi near coil center: {A_phi_sample:.4f} T*m")
    print(f"Max B-field magnitude found in grid: {np.max(Bmag):.4f} T")

    plt.show()
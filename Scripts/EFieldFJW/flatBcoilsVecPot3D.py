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
        axis = np.array([1, 0, 0]) if not np.allclose(a, [1, 0, 0]) else np.array([0, 1, 0])
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

def Aphi_loop(rho, z, R, I):
    if rho < 1e-12:
        return 0.0
    k2 = 4 * R * rho / ((R + rho) ** 2 + z ** 2)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    E = ellipe(k2)
    denom = np.sqrt((R + rho) ** 2 + z ** 2)
    pref = mu_0 * I / (np.pi * np.sqrt(k2))
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
    Aphi /= coil["turns"]
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

def compute_B_field(a, b, turns=10, I=1e6, offset=1.0):
    """Compute Bx, By, Bz, Bmag on XZ plane, plus centerline |B|."""

    raw_coils = [
        ([offset, 0, 0], [1, 0, 0]),
        ([-offset, 0, 0], [-1, 0, 0]),
        ([0, offset, 0], [0, 1, 0]),
        ([0, -offset, 0], [0, -1, 0]),
        ([0, 0, offset], [0, 0, 1]),
        ([0, 0, -offset], [0, 0, -1]),
    ]
    coils = [{"center": np.array(c), "normal": np.array(n), "a": a, "b": b,
              "turns": turns, "I": I, "R": rotation_matrix_from_vectors(np.array(n), np.array([0, 0, 1]))}
             for c, n in raw_coils]

    # Evaluation grid
    x = np.linspace(-1.5, 1.5, 140)
    z = np.linspace(-1.5, 1.5, 140)
    X, Z = np.meshgrid(x, z)
    A = np.zeros((X.shape[0], X.shape[1], 3))

    # Compute vector potential
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            r = np.array([X[i, j], 0.0, Z[i, j]])
            A[i, j] = sum(A_coil_global(r, coil) for coil in coils)

    dx = x[1] - x[0]
    dz = z[1] - z[0]
    Ax, Ay, Az = A[:, :, 0], A[:, :, 1], A[:, :, 2]

    # Curl A -> B
    dAz_dx = np.gradient(Az, dx, axis=1, edge_order=2)
    dAx_dz = np.gradient(Ax, dz, axis=0, edge_order=2)
    dAy_dx = np.gradient(Ay, dx, axis=1, edge_order=2)
    dAy_dz = np.gradient(Ay, dz, axis=0, edge_order=2)

    Bx = -dAy_dz
    By = dAx_dz - dAz_dx
    Bz = dAy_dx
    Bmag = np.sqrt(Bx ** 2 + By ** 2 + Bz ** 2)

    # Extract on-axis Bz directly from grid
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
        (0.05, 0.95),
        (0.15, 0.85),
        (0.05, 0.75)
    ]

    N_turns = 10
    I_current = 1e6
    Lc_offset = 1.0

    # Create figure framework
    fig = plt.figure(figsize=(20, 16), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, width_ratios=[1.1, 1.1, 1])

    # =========================================================
    # Loop over geometries
    # =========================================================

    for row, (a, b) in enumerate(geometries):

        # Axis initializations
        ax1 = fig.add_subplot(gs[row, 0])
        ax2 = fig.add_subplot(gs[row, 1], projection='3d')
        ax3 = fig.add_subplot(gs[row, 2])

        X, Z, x, z, Bx, By, Bz, Bmag, z_line, Bline, t, Bdiag_x, Bdiag_z = compute_B_field(
            a=a, b=b, turns=N_turns, I=I_current, offset=Lc_offset
        )

        # Base log calculations
        floor_low = np.exp(-6)
        floor_high = np.exp(-2)

        logB_ax1 = np.log(np.maximum(Bmag, floor_low))
        logB_ax2 = np.log(np.maximum(Bmag, floor_high))

        if row == 0:
            norm_ax1 = Normalize(vmin=-4, vmax=np.max(logB_ax1))
        else:
            norm_ax1 = Normalize(vmin=-6, vmax=np.max(logB_ax1))

        norm_ax2 = Normalize(vmin=-6, vmax=np.max(logB_ax2))

        # =====================================================
        # COLUMN 1: Streamlines
        # =====================================================

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
            f"a={a:.2f} m, b={b:.2f} m, $L_c$={Lc_offset:.1f} m\n"
            f"I={I_current:.1e} A, N={N_turns}"
        )
        ax1.set_xlabel("x (m)")
        ax1.set_ylabel("z (m)")
        ax1.set_aspect('equal')
        ax1.grid(True)

        # Draw Coils on the 2D plane (Column 1)
        ax1.plot([a, b], [Lc_offset, Lc_offset], 'k', lw=5)
        ax1.plot([a, b], [-Lc_offset, -Lc_offset], 'k', lw=5)
        ax1.plot([-a, -b], [Lc_offset, Lc_offset], 'k', lw=5)
        ax1.plot([-a, -b], [-Lc_offset, -Lc_offset], 'k', lw=5)
        ax1.plot([Lc_offset, Lc_offset], [a, b], 'k', lw=5)
        ax1.plot([Lc_offset, Lc_offset], [-a, -b], 'k', lw=5)
        ax1.plot([-Lc_offset, -Lc_offset], [a, b], 'k', lw=5)
        ax1.plot([-Lc_offset, -Lc_offset], [-a, -b], 'k', lw=5)

        # =====================================================
        # COLUMN 2: 3D Surface of Constant-|B|
        # =====================================================

        surf = ax2.plot_surface(
            X, Z, logB_ax2,
            cmap='plasma',
            norm=norm_ax2,
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            rcount=100, ccount=100
        )

        # Bottom floor shadow projection
        zmin = -6
        ax2.contour(
            X, Z, logB_ax2,
            levels=8,
            cmap='plasma',
            linewidths=1.0,
            offset=zmin
        )

        ax2.set_title("B Field Contours")
        ax2.set_xlabel("x (m)", labelpad=8)
        ax2.set_ylabel("z (m)", labelpad=8)
        ax2.set_zlabel(r'$\log |\vec{B}|$ (T)', labelpad=8)
        ax2.set_zlim(zmin, np.max(logB_ax2))
        ax2.view_init(elev=30, azim=-45)

        # =====================================================
        # COLUMN 3: Line-out Profiles
        # =====================================================

        # Linear Profiles (Left Y-Axis)
        ax3.plot(z_line, Bline, color='navy', lw=2, label="On-Axis $B_z$")
        ax3.plot(t, Bdiag_x, color='forestgreen', lw=1.5, ls='-.', label="Diagonal $B_x$")
        ax3.plot(t, Bdiag_z, color='teal', lw=1.5, ls=':', label="Diagonal $B_z$")

        ax3.set_title("B Field Line-Outs")
        ax3.set_xlabel("Coordinate Position (m)")
        ax3.set_ylabel("Field Strength (T)")
        ax3.grid(True)
        ax3.legend(loc='upper right')

        # Logarithmic Overlay Profile (Right Y-Axis)
        ax3b = ax3.twinx()
        ax3b.plot(
            z_line,
            np.log(np.maximum(np.abs(Bline), 1e-30)),
            color='darkred',
            ls='--',
            lw=1.5
        )
        ax3b.set_ylabel(r'$\log |B_z|$', color='darkred')
        ax3b.tick_params(axis='y', colors='darkred')

    plt.show()
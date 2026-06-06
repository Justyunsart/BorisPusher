"""
3-D magnetic field solver for six flat, multi-turn, hexahedral coils
and eight flat, multi-turn corner coils.
Magnetic analogue of washer electrostatic code.

Computes analytical fields then plots two configurations:
1. Standard XY plane (Z=0)
2. XY plane rotated 45 degrees about the Y-axis (Slicing 4 corner coil centers)

Author:  FJ Wessel
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# --- CONSTANTS & PARAMETERS ---
mu_0 = 4 * np.pi * 1e-7

# 1. Face Coils (All moments outward)
a, b = 0.15, 0.8  # Inner and outer radii [m]
d_face = 1.0  # Distance to face centers [m]
I_face_total = 10 * 1e5  # N = 10, I = 10^5 A
K_face = I_face_total / (b - a)

# 2. Corner Coils (All moments inward / "Anti" configuration)
c, d = 0.15, 0.50  # Inner and outer radii [m]
I_corner_total = 4.5 * 1e5  # balanced flux corners = faces
K_corner = I_corner_total / (d - c)


# --- GEOMETRY MANIFESTS ---
# 6 Face Configurations
face_configs = [
    {'center': np.array([d_face, 0, 0]), 'z_loc': np.array([1, 0, 0]), 'x_loc': np.array([0, 1, 0])},
    {'center': np.array([-d_face, 0, 0]), 'z_loc': np.array([-1, 0, 0]), 'x_loc': np.array([0, 1, 0])},
    {'center': np.array([0, d_face, 0]), 'z_loc': np.array([0, 1, 0]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, -d_face, 0]), 'z_loc': np.array([0, -1, 0]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, 0, d_face]), 'z_loc': np.array([0, 0, 1]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, 0, -d_face]), 'z_loc': np.array([0, 0, -1]), 'x_loc': np.array([1, 0, 0])}
]

# 8 Corner Configurations (Radial distance to a standard cube vertex is sqrt(3))
corner_base_vectors = np.array([
    [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
    [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
])

corner_configs = []
for vec in corner_base_vectors:
    norm_direction = vec / np.linalg.norm(vec)
    center = norm_direction * (d_face * np.sqrt(3))  # Placed at vertex shell radius

    # Magnetic moment points inward -> local z-axis points toward origin
    z_loc = -norm_direction

    # Construct orthogonal base tracking coordinates
    not_z = np.array([1, 0, 0]) if abs(z_loc[0]) < 0.9 else np.array([0, 1, 0])
    x_loc = np.cross(z_loc, not_z)
    x_loc /= np.linalg.norm(x_loc)

    corner_configs.append({'center': center, 'z_loc': z_loc, 'x_loc': x_loc})


def compute_disk_B_kernel(r_l, z_l, r_in, r_out, K_surface):
    """Computes the analytical field components for an arbitrary annular winding profile."""
    if r_l < 1e-6:
        val, _ = quad(lambda rp: rp ** 2 / ((rp ** 2 + z_l ** 2) ** (1.5)), r_in, r_out)
        return 0.0, (mu_0 * K_surface / 2.0) * val

    def integrand_bz(rp):
        d1 = np.sqrt((r_l + rp) ** 2 + z_l ** 2)
        d2 = (r_l - rp) ** 2 + z_l ** 2
        k2 = (4 * r_l * rp) / ((r_l + rp) ** 2 + z_l ** 2)
        if abs(d2) < 1e-6 or abs(k2 - 1.0) < 1e-6: return 0.0
        return (1.0 / d1) * (ellipk(k2) + ((rp ** 2 - r_l ** 2 - z_l ** 2) / d2) * ellipe(k2))

    def integrand_br(rp):
        d1 = np.sqrt((r_l + rp) ** 2 + z_l ** 2)
        d2 = (r_l - rp) ** 2 + z_l ** 2
        k2 = (4 * r_l * rp) / ((r_l + rp) ** 2 + z_l ** 2)
        if abs(d2) < 1e-6 or abs(k2 - 1.0) < 1e-6: return 0.0
        return (1.0 / d1) * (-ellipk(k2) + ((r_l ** 2 + rp ** 2 + z_l ** 2) / d2) * ellipe(k2))

    bz_val, _ = quad(integrand_bz, r_in, r_out, limit=50)
    br_val, _ = quad(integrand_br, r_in, r_out, limit=50)

    bz = (mu_0 * K_surface / (2.0 * np.pi)) * bz_val
    br = (mu_0 * K_surface / (2.0 * np.pi)) * (z_l / r_l) * br_val
    return br, bz


def get_total_B(X, Y, Z):
    """Accumulates global 3D field contributions from the 6 face and 8 corner coils."""
    B_total = np.zeros(3)
    P_global = np.array([X, Y, Z])

    # Contribution from 6 Face Coils (Outward)
    for face in face_configs:
        P_rel = P_global - face['center']
        z_l = np.dot(P_rel, face['z_loc'])
        x_l = np.dot(P_rel, face['x_loc'])
        y_loc_axis = np.cross(face['z_loc'], face['x_loc'])
        y_l = np.dot(P_rel, y_loc_axis)
        r_l = np.sqrt(x_l ** 2 + y_l ** 2)

        br_l, bz_l = compute_disk_B_kernel(r_l, z_l, a, b, K_face)
        bx_l = br_l * (x_l / r_l) if r_l > 1e-6 else 0.0
        by_l = br_l * (y_l / r_l) if r_l > 1e-6 else 0.0
        B_total += bz_l * face['z_loc'] + bx_l * face['x_loc'] + by_l * y_loc_axis

    # Contribution from 8 Corner Coils (Inward Anti-Coils)
    for corner in corner_configs:
        P_rel = P_global - corner['center']
        z_l = np.dot(P_rel, corner['z_loc'])
        x_l = np.dot(P_rel, corner['x_loc'])
        y_loc_axis = np.cross(corner['z_loc'], corner['x_loc'])
        y_l = np.dot(P_rel, y_loc_axis)
        r_l = np.sqrt(x_l ** 2 + y_l ** 2)

        br_l, bz_l = compute_disk_B_kernel(r_l, z_l, c, d, K_corner)
        bx_l = br_l * (x_l / r_l) if r_l > 1e-6 else 0.0
        by_l = br_l * (y_l / r_l) if r_l > 1e-6 else 0.0
        B_total += bz_l * corner['z_loc'] + bx_l * corner['x_loc'] + by_l * y_loc_axis

    return B_total


# --- GRID MATRIX SETUP ---
grid_res = 55
xy_range = np.linspace(-2.2, 2.2, grid_res)
U, V = np.meshgrid(xy_range, xy_range)

# Plot 1 Canvas Slices (Standard Z=0 plane)
Bx_p1 = np.zeros(U.shape)
By_p1 = np.zeros(U.shape)

# Plot 2 Canvas Slices (45-degree rotation about global Y-axis)
Bu_p2 = np.zeros(U.shape)
Bv_p2 = np.zeros(U.shape)

print("Evaluating Plot 1 fields (Standard XY Midplane)...")
for i in range(grid_res):
    for j in range(grid_res):
        B_vec = get_total_B(U[i, j], V[i, j], 0.0)
        Bx_p1[i, j] = B_vec[0]
        By_p1[i, j] = B_vec[1]

print("Evaluating Plot 2 fields (45-degree Y-Axis Rotated Corner Slice)...")
theta = np.radians(45.0)
cos_t, sin_t = np.cos(theta), np.sin(theta)

for i in range(grid_res):
    for j in range(grid_res):
        # Map local tracking grid (u, v) into global 3D space via Y-rotation matrix
        x_glob = U[i, j] * cos_t
        y_glob = V[i, j]
        z_glob = U[i, j] * sin_t

        B_vec = get_total_B(x_glob, y_glob, z_glob)

        # Project global Cartesian B field components onto local viewing axes
        Bu_p2[i, j] = B_vec[0] * cos_t + B_vec[2] * sin_t
        Bv_p2[i, j] = B_vec[1]

# Streamline seed matrices
seed_u, seed_v = np.meshgrid(np.linspace(-2.0, 2.0, 18), np.linspace(-2.0, 2.0, 18))
seeds = np.vstack([seed_u.ravel(), seed_v.ravel()]).T

# =============================================================================
# PLOT 1: STANDARD XY PLANE
# =============================================================================
fig1, ax1 = plt.subplots(figsize=(11, 11))
B_mag1 = np.sqrt(Bx_p1**2 + By_p1**2)

contour1 = ax1.contourf(U, V, B_mag1, levels=50, cmap='plasma', alpha=0.4)
cbar = fig1.colorbar(contour1, ax=ax1, shrink=0.85, pad=0.03)
cbar.set_label(r'Field Intensity $|\mathbf{B}|$ [Tesla]', fontsize=11)
ax1.streamplot(U, V, Bx_p1, By_p1, color='#2c3e50', linewidth=1.1,
              density=2.0, arrowstyle='->', arrowsize=0.9, start_points=seeds)

# Overlay face coils cross-sections intersecting Z=0
ax1.plot([d_face, d_face], [a, b], color='#4b0082', linewidth=5, label='Face Coils (In-Plane)')
ax1.plot([d_face, d_face], [-a, -b], color='#4b0082', linewidth=5)
ax1.plot([-d_face, -d_face], [a, b], color='#4b0082', linewidth=5)
ax1.plot([-d_face, -d_face], [-a, -b], color='#4b0082', linewidth=5)
ax1.plot([a, b], [d_face, d_face], color='#4b0082', linewidth=5)
ax1.plot([-a, -b], [d_face, d_face], color='#4b0082', linewidth=5)
ax1.plot([a, b], [-d_face, -d_face], color='#4b0082', linewidth=5)
ax1.plot([-a, -b], [-d_face, -d_face], color='#4b0082', linewidth=5)

ax1.scatter(0, 0, color='gold', s=150, edgecolors='black', label='Central Null Core (B = 0)', zorder=10)
ax1.set_xlabel('Global X Axis [m]')
ax1.set_ylabel('Global Y Axis [m]')
ax1.set_title('Plot 1: Magnetic Fields Lines and Contours in the Standard $(X, Y, Z=0)$ Midplane\n(Slicing Directly Through 4 Face Coil Centers)', fontsize=11, pad=15)
ax1.legend(loc='upper right')
ax1.set_xlim(-2.2, 2.2)
ax1.set_ylim(-2.2, 2.2)
ax1.grid(True, linestyle=':', alpha=0.3)

# =============================================================================
# PLOT 2: 45-DEGREE Y-AXIS ROTATED PLANE (CORRECTED GEOMETRY ORIENTATIONS)
# =============================================================================
fig2, ax2 = plt.subplots(figsize=(11, 11))
B_mag2 = np.sqrt(Bu_p2 ** 2 + Bv_p2 ** 2)

contour2 = ax2.contourf(U, V, B_mag2, levels=50, cmap='plasma', alpha=0.4)
cbar = fig1.colorbar(contour2, ax=ax2, shrink=0.85, pad=0.03)
cbar.set_label(r'Field Intensity $|\mathbf{B}|$ [Tesla]', fontsize=11)
ax2.streamplot(U, V, Bu_p2, Bv_p2, color='#2c3e50', linewidth=1.1,
               density=2.0, arrowstyle='->', arrowsize=0.9, start_points=seeds)

# Analytical geometric parameters for the cutting plane
d_corner_plane = d_face * np.sqrt(2)
alpha_angle = np.arctan(1.0 / np.sqrt(2.0))  # Tilt angle of the corner coil faces relative to plane

# Explicitly trace the 4 corner coils intersecting this plane using their true global parities
# This ensures that the forward/backward slant properties are perfectly preserved in all 4 quadrants
corner_plane_crossings = [
    {'u': d_corner_plane, 'v': d_face, 'slant': -1},  # Top-Right (+X, +Y, +Z)
    {'u': -d_corner_plane, 'v': d_face, 'slant': 1},  # Top-Left (-X, +Y, -Z)
    {'u': d_corner_plane, 'v': -d_face, 'slant': 1},  # Bottom-Right (+X, -Y, +Z)
    {'u': -d_corner_plane, 'v': -d_face, 'slant': -1}  # Bottom-Left (-X, -Y, -Z)
]

labeled_c = False
for coil in corner_plane_crossings:
    u_c = coil['u']
    v_c = coil['v']
    s = coil['slant']  # Spatial parity toggle controlling the geometric tilt

    label_txt = 'Corner Anti-Coils (In-Plane)' if not labeled_c else ""

    # Render the upper and lower edge boundaries of the flat annular washer profile
    ax2.plot([u_c + s * c * np.sin(alpha_angle), u_c + s * d * np.sin(alpha_angle)],
             [v_c + c * np.cos(alpha_angle), v_c + d * np.cos(alpha_angle)],
             color='#e74c3c', linewidth=4, label=label_txt)
    ax2.plot([u_c - s * c * np.sin(alpha_angle), u_c - s * d * np.sin(alpha_angle)],
             [v_c - c * np.cos(alpha_angle), v_c - d * np.cos(alpha_angle)],
             color='#e74c3c', linewidth=4)
    labeled_c = True

ax2.scatter(0, 0, color='gold', s=150, edgecolors='black', label='Central Null Core (B = 0)', zorder=10)
ax2.set_xlabel('Rotated Plane Horizontal Axis (X-Z Projection Matrix) [m]')
ax2.set_ylabel('Rotated Plane Vertical Axis (Global Y Axis) [m]')
ax2.set_title(
    'Plot 2: Magnetic Field Lines and Contours in the 45-Degree Y-Axis Rotated Slice\n(Slicing Directly Through 4 Corner Anti-Coil Centers)',
    fontsize=11, pad=15)
ax2.legend(loc='upper right')
ax2.set_xlim(-2.2, 2.2)
ax2.set_ylim(-2.2, 2.2)
ax2.grid(True, linestyle=':', alpha=0.3)

plt.show()
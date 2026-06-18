"""
3-D magnetic field solver for six flat, multi-turn, hexahedral coils
and eight flat, multi-turn corner coils. Magnetic analogue of washer electrostatic code.

Computes vector potential A then evaluates B = curl(A).
Plots the differential vector field in the XY plane.

Author:  FJ Wessel
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# --- CONSTANTS & PARAMETERS ---
mu_0 = 4 * np.pi * 1e-7

# 1. Face Coils Geometry (All moments outward)
a, b = 0.2, 0.8
d_face = 1.0
I_face_total = 10 * 1e5
K_face = I_face_total / (b - a)

# 2. Corner Coils Geometry (All moments inward / "Anti" configuration)
c, d = 0.15, 0.50
I_corner_total = 5 * 1e5
K_corner = I_corner_total / (d - c)

# --- GEOMETRY MANIFESTS ---
face_configs = [
    {'center': np.array([d_face, 0, 0]), 'z_loc': np.array([1, 0, 0]), 'x_loc': np.array([0, 1, 0])},
    {'center': np.array([-d_face, 0, 0]), 'z_loc': np.array([-1, 0, 0]), 'x_loc': np.array([0, 1, 0])},
    {'center': np.array([0, d_face, 0]), 'z_loc': np.array([0, 1, 0]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, -d_face, 0]), 'z_loc': np.array([0, -1, 0]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, 0, d_face]), 'z_loc': np.array([0, 0, 1]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, 0, -d_face]), 'z_loc': np.array([0, 0, -1]), 'x_loc': np.array([1, 0, 0])}
]

corner_base_vectors = np.array([
    [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
    [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
])

corner_configs = []
for vec in corner_base_vectors:
    norm_direction = vec / np.linalg.norm(vec)
    center = norm_direction * (d_face * np.sqrt(3))
    z_loc = -norm_direction
    not_z = np.array([1, 0, 0]) if abs(z_loc[0]) < 0.9 else np.array([0, 1, 0])
    x_loc = np.cross(z_loc, not_z)
    x_loc /= np.linalg.norm(x_loc)
    corner_configs.append({'center': center, 'z_loc': z_loc, 'x_loc': x_loc})


def compute_disk_B_kernel(r_l, z_l, r_in, r_out, K_surface):
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
    return (mu_0 * K_surface / (2.0 * np.pi)) * (z_l / r_l) * br_val, (mu_0 * K_surface / (2.0 * np.pi)) * bz_val


def get_B_components(X, Y, Z, include_corners=True):
    """Calculates global B components, optionally skipping corner coils."""
    B_total = np.zeros(3)
    P_global = np.array([X, Y, Z])

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

    if include_corners:
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


# --- GRID GENERATION (Z = 0) ---
grid_res = 50
xy_range = np.linspace(-2.2, 2.2, grid_res)
X_mesh, Y_mesh = np.meshgrid(xy_range, xy_range)

Bx_diff = np.zeros(X_mesh.shape)
By_diff = np.zeros(X_mesh.shape)

print("Calculating differential field vector maps...")
for i in range(grid_res):
    for j in range(grid_res):
        x, y = X_mesh[i, j], Y_mesh[i, j]

        # Sample total hybrid field and face baseline field
        B_14 = get_B_components(x, y, 0.0, include_corners=True)
        B_6 = get_B_components(x, y, 0.0, include_corners=False)

        # Isolate delta vectors
        Bx_diff[i, j] = B_14[0] - B_6[0]
        By_diff[i, j] = B_14[1] - B_6[1]

# --- PLOTTING ---
fig, ax = plt.subplots(figsize=(11, 11))

# Background color mapping representing the magnitude of the added corner field
Delta_B_mag = np.sqrt(Bx_diff ** 2 + By_diff ** 2)
contour = ax.contourf(X_mesh, Y_mesh, Delta_B_mag, levels=50, cmap='plasma', alpha=0.2)
cbar = fig.colorbar(contour, ax=ax, shrink=0.85, pad=0.03)
cbar.set_label(r'Differential Field Intensity $|\mathbf{B}_{\mathrm{diff}}|$ [Tesla]', fontsize=11)

# Uniformly distributed seed matrix for streamline continuity
seed_x, seed_y = np.meshgrid(np.linspace(-2.0, 2.0, 16), np.linspace(-2.0, 2.0, 16))
seeds = np.vstack([seed_x.ravel(), seed_y.ravel()]).T

# Plot the Delta Streamlines
ax.streamplot(X_mesh, Y_mesh, Bx_diff, By_diff, color='#4b0082', linewidth=1.2,
              density=1.8, arrowstyle='->', arrowsize=1.0, start_points=seeds)

# Overlay Cross-Sections of ONLY the Coils that physically intersect Z=0
# Coils centered on the X-axis (Face Coils at X = +1 and X = -1)
ax.plot([d_face, d_face], [a, b], color='black', linewidth=5, label='Face Coils (In-Plane Baseline)')
ax.plot([d_face, d_face], [-a, -b], color='black', linewidth=5)
ax.plot([-d_face, -d_face], [a, b], color='black', linewidth=5)
ax.plot([-d_face, -d_face], [-a, -b], color='black', linewidth=5)

# Coils centered on the Y-axis (Face Coils at Y = +1 and Y = -1)
ax.plot([a, b], [d_face, d_face], color='black', linewidth=5)
ax.plot([-a, -b], [d_face, d_face], color='black', linewidth=5)
ax.plot([a, b], [-d_face, -d_face], color='black', linewidth=5)
ax.plot([-a, -b], [-d_face, -d_face], color='black', linewidth=5)

ax.set_xlabel('Global X Axis [m]', fontsize=11)
ax.set_ylabel('Global Y Axis [m]', fontsize=11)
ax.set_title(
    r'Differential Magnetic Field Map: $\mathbf{B}_{\mathrm{diff}} = \mathbf{B}_{14\mathrm{-coil}} - \mathbf{B}_{6\mathrm{-coil}}$' + '\n(Isolated Structural Footprint of Corner Plugs Projected on $Z=0$ Plane)',
    fontsize=12, pad=15)
ax.legend(loc='upper right')
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()
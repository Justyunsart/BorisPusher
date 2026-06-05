"""
3-D magnetic field solver for six flat, multi-turn, hexahedral coils
and eight flat, multi-turn corner coils.
Magnetic analogue of washer electrostatic code.

Computes vector potential A then evaluates B = curl(A).
Plots in XY plane.

Author:  FJ Wessel
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# --- CONSTANTS & PARAMETERS ---
mu_0 = 4 * np.pi * 1e-7

# 1. Face Coils (All moments outward)
a, b = 0.2, 0.8  # Inner and outer radii [m]
d_face = 1.0  # Distance to face centers [m]
I_face_total = 10 * 1e5  # N = 10, I = 10^5 A
K_face = I_face_total / (b - a)

# 2. Corner Coils (All moments inward / "Anti" configuration)
c, d = 0.15, 0.50  # Inner and outer radii [m]
I_corner_total = -5 * 1e5  # N_2 = 5, I_2 = 10^5 A
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


# --- GRID GENERATION (Z = 0) ---
grid_res = 55
xy_range = np.linspace(-2.2, 2.2, grid_res)
X_mesh, Y_mesh = np.meshgrid(xy_range, xy_range)

Bx = np.zeros(X_mesh.shape)
By = np.zeros(X_mesh.shape)

print("Computing analytical fields for the 14-coil hybrid configuration...")
for i in range(grid_res):
    for j in range(grid_res):
        B_vec = get_total_B(X_mesh[i, j], Y_mesh[i, j], 0.0)
        Bx[i, j] = B_vec[0]
        By[i, j] = B_vec[1]

# --- VISUALIZATION (CORRECTED PLANE GEOMETRY) ---
fig, ax = plt.subplots(figsize=(11, 11))

B_mag = np.sqrt(Bx**2 + By**2)
ax.contourf(X_mesh, Y_mesh, B_mag, levels=50, cmap='plasma', alpha=0.15)

contour = ax.contourf(X_mesh, Y_mesh, B_mag, levels=50, cmap='plasma', alpha=0.2)
cbar = fig.colorbar(contour, ax=ax, shrink=0.85, pad=0.03)
cbar.set_label(r'Field Intensity $|\mathbf{B}_{\mathrm{diff}}|$ [Tesla]', fontsize=11)

# Uniformly distributed seed matrix for streamline continuity
seed_x, seed_y = np.meshgrid(np.linspace(-2.0, 2.0, 18), np.linspace(-2.0, 2.0, 18))
seeds = np.vstack([seed_x.ravel(), seed_y.ravel()]).T

# Plot Streamlines passing through the Z=0 plane
ax.streamplot(X_mesh, Y_mesh, Bx, By, color='#2c3e50', linewidth=1.1,
              density=2.0, arrowstyle='->', arrowsize=0.9, start_points=seeds)

# Overlay Cross-Sections of ONLY the Coils that physically intersect Z=0
# Coils centered on the X-axis (Face Coils at X = +1 and X = -1)
ax.plot([d_face, d_face], [a, b], color='#4b0082', linewidth=5, label='Face Coils (In-Plane)')
ax.plot([d_face, d_face], [-a, -b], color='#4b0082', linewidth=5)
ax.plot([-d_face, -d_face], [a, b], color='#4b0082', linewidth=5)
ax.plot([-d_face, -d_face], [-a, -b], color='#4b0082', linewidth=5)

# Coils centered on the Y-axis (Face Coils at Y = +1 and Y = -1)
ax.plot([a, b], [d_face, d_face], color='#4b0082', linewidth=5)
ax.plot([-a, -b], [d_face, d_face], color='#4b0082', linewidth=5)
ax.plot([a, b], [-d_face, -d_face], color='#4b0082', linewidth=5)
ax.plot([-a, -b], [-d_face, -d_face], color='#4b0082', linewidth=5)

# (Note: Corner coils at Z = +1 and Z = -1 are omitted here as they do not intersect this plane)

ax.scatter(0, 0, color='gold', s=150, edgecolors='black', label='Central Null Core (B = 0)', zorder=10)

ax.set_xlabel('Global X Axis [m]')
ax.set_ylabel('Global Y Axis [m]')
ax.set_title('14-Coil Interlocking Grid: Magnetic Field Lines in the $Z=0$ Midplane\n(Corner Plug Fields Projected out of Plane)', fontsize=11, pad=15)
ax.legend(loc='upper right')
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()

# Sphericity and Dipole Alignment Check
print("--- COIL POLARITY VERIFICATION MATRIX ---")

for idx, face in enumerate(face_configs):
    alignment = np.dot(face['center'], face['z_loc'])
    direction = "OUTWARD" if alignment > 0 else "INWARD"
    print(f"Face Coil {idx+1}: Center={face['center']}, Moment Vector={face['z_loc']} -> {direction}")

for idx, corner in enumerate(corner_configs):
    alignment = np.dot(corner['center'], corner['z_loc'])
    direction = "OUTWARD" if alignment > 0 else "INWARD"
    # Rounding clean print outputs for readable coordinate vectors
    rounded_center = np.round(corner['center'], 3)
    rounded_z = np.round(corner['z_loc'], 3)
    print(f"Corner Coil {idx+1}: Center={rounded_center}, Moment Vector={rounded_z} -> {direction}")
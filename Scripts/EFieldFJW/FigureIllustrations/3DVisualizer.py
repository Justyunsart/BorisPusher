"""
3-D Magnetic Field Isosurface Visualizer for a 14-Coil Polywell Trap.
Generates a 3D volumetric grid of |B| and uses Plotly to render
interactive 3D isosurfaces ("magnetic bottle walls").

Author: FJ Wessel & AI Collaborator
"""

import numpy as np
import plotly.graph_objects as go
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# --- CONSTANTS & PARAMETERS ---
mu_0 = 4 * np.pi * 1e-7

# 1. Face Coils (All moments outward)
a, b = 0.2, 0.8
d_face = 1.0
I_face_total = 10 * 1e5
K_face = I_face_total / (b - a)

# 2. Corner Coils (All moments inward / "Anti" configuration)
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

    bz_val, _ = quad(integrand_bz, r_in, r_out, limit=30)
    br_val, _ = quad(integrand_br, r_in, r_out, limit=30)
    return (mu_0 * K_surface / (2.0 * np.pi)) * (z_l / r_l) * br_val, (mu_0 * K_surface / (2.0 * np.pi)) * bz_val

def get_total_B_mag(X, Y, Z):
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

    return np.linalg.norm(B_total)

# --- GENERATE 3D VOLUMETRIC MESH ---
# Lowering resolution slightly to 25^3 to optimize multi-dimensional integration times
grid_res = 25
bound = 1.8
span = np.linspace(-bound, bound, grid_res)
X, Y, Z = np.meshgrid(span, span, span, indexing='ij')

B_mag_volume = np.zeros(X.shape)

print(f"Populating {grid_res}^3 volumetric field matrix. Please hold...")
for i in range(grid_res):
    print(f"Processing slice {i+1} of {grid_res}...")
    for j in range(grid_res):
        for k in range(grid_res):
            B_mag_volume[i, j, k] = get_total_B_mag(X[i,j,k], Y[i,j,k], Z[i,j,k])

# --- 3D INTERACTIVE PLOTLY ISOSURFACE ---
print("Rendering interactive 3D visualization window...")

# Define threshold values for the isosurface levels (in Tesla)
# Adjust these depending on the exact peak fields you wish to display
isomin_val = 0.05
isomax_val = 0.45

fig = go.Figure(data=go.Isosurface(
    x=X.flatten(),
    y=Y.flatten(),
    z=Z.flatten(),
    value=B_mag_volume.flatten(),
    isomin=isomin_val,
    isomax=isomax_val,
    surface_count=4,          # Renders 4 concentric shell "nested layers"
    opacity=0.4,              # Translucent shells to see inner core structures
    caps=dict(x_show=False, y_show=False, z_show=False), # Turn off boundary box clipping caps
    colorscale='inferno',
    colorbar=dict(title='|B| [Tesla]')
))

# Overlay a central marker representing the geometric null core
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers',
    marker=dict(
        size=10,
        color='gold',
        line=dict(color='black', width=2)  # Correct Plotly outline syntax
    ),
    name='B=0 Well Core'
))

# Layout configurations for clean 3D aspect tracking
fig.update_layout(
    title='14-Coil Polywell Configuration: Interactive 3D |B| Isosurfaces',
    scene=dict(
        xaxis_title='Global X Axis [m]',
        yaxis_title='Global Y Axis [m]',
        zaxis_title='Global Z Axis [m]',
        aspectmode='cube'
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

# Open in browser window or output to local notebook frame
fig.show()
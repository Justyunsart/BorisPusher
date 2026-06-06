"""
3-D Magnetic Field Isosurface and Hardware Visualizer for a 14-Coil Polywell Trap.
Generates a 3D volumetric grid of |B|, renders interactive 3D isosurfaces,
and overlays explicit 3D wireframe rings representing the physical coils.

Author: FJ Wessel & AI Collaborator
"""

import numpy as np
import plotly.graph_objects as go
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# --- CONSTANTS & PARAMETERS ---
mu_0 = 4 * np.pi * 1e-7

# 1. Face Coils (All moments outward)
r_face_in = 0.15
r_face_out = 0.85
d_face = 1.3
I_face_total = 10 * 1e5
K_face = I_face_total / (r_face_out - r_face_in)

# 2. Corner Coils (All moments inward / "Anti" configuration)
r_corner_in = 0.15
r_corner_out = 0.50
d_corner = 1.6
I_corner_total = -4.5 * 1e5 # sets the total flux phi_corners =  0.75 x phi_faces
K_corner = I_corner_total / (r_corner_out - r_corner_in)

# --- GEOMETRY MANIFESTS ---
face_configs = [
    {'center': np.array([d_face, 0, 0]), 'z_loc': np.array([1, 0, 0]), 'x_loc': np.array([0, 1, 0])},
    {'center': np.array([-d_face, 0, 0]), 'z_loc': np.array([-1, 0, 0]), 'x_loc': np.array([0, 1, 0])},
    {'center': np.array([0, d_face, 0]), 'z_loc': np.array([0, 1, 0]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, -d_face, 0]), 'z_loc': np.array([0, -1, 0]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, 0, d_face]), 'z_loc': np.array([0, 0, 1]), 'x_loc': np.array([1, 0, 0])},
    {'center': np.array([0, 0, -d_face]), 'z_loc': np.array([0, 0, -1]), 'x_loc': np.array([1, 0, 0])}
]

corner_raw = np.array([
    [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
    [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
])

corner_configs = []
for vec in corner_raw:
    norm_direction = vec / np.linalg.norm(vec)
    center = norm_direction * d_corner
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

        br_l, bz_l = compute_disk_B_kernel(r_l, z_l, r_face_in, r_face_out, K_face)
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

        br_l, bz_l = compute_disk_B_kernel(r_l, z_l, r_corner_in, r_corner_out, K_corner)
        bx_l = br_l * (x_l / r_l) if r_l > 1e-6 else 0.0
        by_l = br_l * (y_l / r_l) if r_l > 1e-6 else 0.0
        B_total += bz_l * corner['z_loc'] + bx_l * corner['x_loc'] + by_l * y_loc_axis

    return np.linalg.norm(B_total)

def get_3d_ring_points(center, normal, radius, num_pts=80):
    """Generates 3D coordinates tracing a circle around a given center normal."""
    n = normal / np.linalg.norm(normal)
    not_n = np.array([1, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(n, not_n)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)

    theta = np.linspace(0, 2 * np.pi, num_pts)
    pts = np.array([center + radius * np.cos(t) * u + radius * np.sin(t) * v for t in theta])
    return pts[:, 0], pts[:, 1], pts[:, 2]

# --- GENERATE 3D VOLUMETRIC MESH ---
grid_res = 24
bound = 2.0
span = np.linspace(-bound, bound, grid_res)
X, Y, Z = np.meshgrid(span, span, span, indexing='ij')

B_mag_volume = np.zeros(X.shape)

print(f"Populating {grid_res}^3 volumetric field matrix...")
for i in range(grid_res):
    print(f"Processing slice {i+1} of {grid_res}...")
    for j in range(grid_res):
        for k in range(grid_res):
            B_mag_volume[i, j, k] = get_total_B_mag(X[i,j,k], Y[i,j,k], Z[i,j,k])

# --- BUILD PLOTLY CANVAS ---
print("Rendering interactive 3D visualization window...")
isomin_val = 0.04
isomax_val = 0.35

fig = go.Figure()

# 1. Add Volumetric Isosurfaces
fig.add_trace(go.Isosurface(
    x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
    value=B_mag_volume.flatten(),
    isomin=isomin_val, isomax=isomax_val,
    surface_count=4, opacity=0.3,
    caps=dict(x_show=False, y_show=False, z_show=False),
    colorscale='inferno', colorbar=dict(title='|B| [Tesla]', x=1.05)
))

# 2. Overlay the 6 Face Coils (Plotted as Outer Diameters using Deep Purple/Indigo)
face_color = '#4b0082'
for idx, face in enumerate(face_configs):
    rx, ry, rz = get_3d_ring_points(face['center'], face['z_loc'], r_face_out)
    fig.add_trace(go.Scatter3d(
        x=rx, y=ry, z=rz, mode='lines',
        line=dict(color=face_color, width=5),
        name='Face Coil OD' if idx == 0 else "",
        showlegend=True if idx == 0 else False
    ))

# 3. Overlay the 8 Corner Coils (Plotted as Outer Diameters using Bright Orange)
corner_color = '#ff8c00'
for idx, corner in enumerate(corner_configs):
    rx, ry, rz = get_3d_ring_points(corner['center'], corner['z_loc'], r_corner_out)
    fig.add_trace(go.Scatter3d(
        x=rx, y=ry, z=rz, mode='lines',
        line=dict(color=corner_color, width=4),
        name='Corner Anti-Coil OD' if idx == 0 else "",
        showlegend=True if idx == 0 else False
    ))

# 4. Corrected Null Core Marker
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0], mode='markers',
    marker=dict(size=8, color='gold', line=dict(color='black', width=2)),
    name='B=0 Well Core'
))

# Canvas framing configurations
fig.update_layout(
    title='14-Coil Polywell Tracker: 3D Isosurfaces mapped over Hardware Profiles',
    scene=dict(
        xaxis=dict(title='Global X Axis [m]', range=[-bound, bound]),
        yaxis=dict(title='Global Y Axis [m]', range=[-bound, bound]),
        zaxis=dict(title='Global Z Axis [m]', range=[-bound, bound]),
        aspectmode='cube'
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

fig.show()
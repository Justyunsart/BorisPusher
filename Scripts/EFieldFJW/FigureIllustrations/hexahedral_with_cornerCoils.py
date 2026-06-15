import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.cm as cm

# --- EXTENSION TO LOAD SCIENTIFIC COLORMAPS SAFELY ---
try:
    import cmcrameri.cm as cmc

    cmap_face_name = 'cmc.berlin'
    cmap_corner_name = 'cmc.berlin_r'  # Reversed variant
except ImportError:
    print("Warning: cmcrameri not installed. Falling back to 'coolwarm'.")
    cmap_face_name = 'coolwarm'
    cmap_corner_name = 'coolwarm_r'  # Reversed variant

# --- CONFIGURATION ---
r_face_in = 0.15
r_face_out = 0.85
d_face = 1.3

r_corner_in = 0.3
r_corner_out = 0.6
d_corner = 1.6

# 1. Define Geometry Positions
face_normals = np.array([
    [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]
])
face_centers = face_normals * d_face

corner_raw = np.array([
    [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
    [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
])
corner_normals = np.array([v / np.linalg.norm(v) for v in corner_raw])
corner_centers = corner_normals * d_corner

cube_edges = [
    (0, 1), (1, 3), (3, 2), (2, 0),
    (4, 5), (5, 7), (7, 6), (6, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]


# 2. Upgraded Function to generate a gradient-mapped flat annular disk
def generate_gradient_disk(normal, center, r_in, r_out, colormap_name, alpha_val, num_points=60):
    n = normal / np.linalg.norm(normal)
    not_n = np.array([1, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(n, not_n)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)

    theta = np.linspace(0, 2 * np.pi, num_points)

    # Calculate ring segments to apply radial colors mapping
    r_steps = 15
    r_vals = np.linspace(r_in, r_out, r_steps)

    try:
        cmap = plt.get_cmap(colormap_name)
    except ValueError:
        cmap = cm.get_cmap(colormap_name)

    norm = plt.Normalize(vmin=r_in, vmax=r_out)

    collections = []
    for r_idx in range(r_steps - 1):
        ri = r_vals[r_idx]
        ro = r_vals[r_idx + 1]

        # Determine segment color based on intermediate radius position
        color = cmap(norm((ri + ro) / 2.0))

        inner_pts = np.array([center + ri * np.cos(t) * u + ri * np.sin(t) * v for t in theta])
        outer_pts = np.array([center + ro * np.cos(t) * u + ro * np.sin(t) * v for t in theta])

        polygons = []
        for i in range(num_points - 1):
            face = [inner_pts[i], inner_pts[i + 1], outer_pts[i + 1], outer_pts[i]]
            polygons.append(face)

        collection = Poly3DCollection(polygons, facecolors=color, edgecolors='none', alpha=alpha_val)
        collections.append(collection)

    return collections


# 3. Setup Plotting Canvas
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig = plt.figure(figsize=(11, 11), facecolor='white')
ax = fig.add_subplot(111, projection='3d', facecolor='white')

arrow_length = 0.35

# Presentation Palette Accent Elements
color_core = "#00F5D4"  # Electric Cyan
color_grid = "#94A3B8"  # Slate Gray
color_arrow = "#000000"  # Clean Black for high contrast

# 4. Draw Inscribed Dotted Reference Cube
for edge in cube_edges:
    ax.plot3D(*zip(corner_centers[edge[0]], corner_centers[edge[1]]),
              color=color_grid, linewidth=1.0, linestyle="--", alpha=0.4, zorder=1)

# 5. Plot Face Disks (Outward Moments - Normal Berlin Gradient)
labeled_f = False
for norm, center in zip(face_normals, face_centers):
    disks = generate_gradient_disk(norm, center, r_face_in, r_face_out, cmap_face_name, alpha_val=0.75)
    for col in disks:
        ax.add_collection3d(col)

    ax.quiver(center[0], center[1], center[2], norm[0] * arrow_length, norm[1] * arrow_length, norm[2] * arrow_length,
              color=color_arrow, linewidth=3.0, arrow_length_ratio=0.25, zorder=5,
              label="Face Disks (+ Outward)" if not labeled_f else "")
    labeled_f = True

# 6. Plot Corner Disks (Inward Moments - REVERSED Berlin Gradient)
labeled_c = False
for norm, center in zip(corner_normals, corner_centers):
    disks = generate_gradient_disk(norm, center, r_corner_in, r_corner_out, cmap_corner_name, alpha_val=0.55)
    for col in disks:
        ax.add_collection3d(col)

    ax.quiver(center[0], center[1], center[2], -norm[0] * arrow_length, -norm[1] * arrow_length,
              -norm[2] * arrow_length,
              color=color_arrow, linewidth=2.5, arrow_length_ratio=0.25, zorder=5,
              label="Corner Disks (- Inward)" if not labeled_c else "")
    labeled_c = True

    ax.plot3D([0, center[0]], [0, center[1]], [0, center[2]],
              color="#A5B4FC", linewidth=0.8, linestyle=":", alpha=0.3, zorder=2)

# Highlight core null point
ax.scatter3D(0, 0, 0, color=color_core, s=220, edgecolors='#0F172A', linewidths=1.5,
             label="Isotropic B = 0 Core Well", zorder=10)

# 7. Formatting and Bounds
ax.set_xlabel('X Axis', fontsize=11, labelpad=10, color="#334155")
ax.set_ylabel('Y Axis', fontsize=11, labelpad=10, color="#334155")
ax.set_zlabel('Z Axis', fontsize=11, labelpad=10, color="#334155")
ax.set_title('14-Coil Polywell Grid Geometry', fontsize=16, fontweight='bold', pad=25, color="#1E293B")

ax.legend(loc="upper right", bbox_to_anchor=(1.1, 0.9), frameon=True, facecolor='white', edgecolor='#E2E8F0',
          fontsize=10)

max_val = (d_corner + r_corner_out + 0.2)
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

# Maintain True Square Cube Aspect Ratio
ax.set_box_aspect([1, 1, 1])

ax.view_init(elev=20, azim=45)

# Clean Pane Formatting
ax.xaxis.set_pane_color((0.98, 0.98, 0.98, 1.0))
ax.yaxis.set_pane_color((0.98, 0.98, 0.98, 1.0))
ax.zaxis.set_pane_color((0.98, 0.98, 0.98, 1.0))
ax.grid(True, linestyle=':', alpha=0.4, color="#CBD5E1")

plt.tight_layout()
plt.show()
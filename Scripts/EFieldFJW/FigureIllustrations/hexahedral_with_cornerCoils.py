import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- CONFIGURATION ---
# Dimensions for the Face Coils (Inner Radius and Outer Radius)
r_face_in = 0.15
r_face_out = 0.85
d_face = 1.3  # Distance to face centers

# Dimensions for the Corner Coils (Inner Radius and Outer Radius)
r_corner_in = 0.15
r_corner_out = 0.50
d_corner = 1.6  # Distance to corner vertices

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


# 2. Function to generate a solid flat annular disk with a uniform color
def generate_flat_disk(normal, center, r_in, r_out, color, num_points=60):
    n = normal / np.linalg.norm(normal)
    not_n = np.array([1, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(n, not_n)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)

    theta = np.linspace(0, 2 * np.pi, num_points)

    inner_pts = np.array([center + r_in * np.cos(t) * u + r_in * np.sin(t) * v for t in theta])
    outer_pts = np.array([center + r_out * np.cos(t) * u + r_out * np.sin(t) * v for t in theta])

    polygons = []
    for i in range(num_points - 1):
        face = [inner_pts[i], inner_pts[i + 1], outer_pts[i + 1], outer_pts[i]]
        polygons.append(face)

    # Standard alpha and edge/face properties for a clean uniform look
    collection = Poly3DCollection(polygons, facecolors=color, edgecolors=color, linewidths=0.5, alpha=0.85)
    return collection


# 3. Setup Plotting Canvas
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

arrow_length = 0.35
color_face   = "#d97706"   # metallic copper
color_corner = "#008080"   # dark orange

# 4. Draw Inscribed Dotted Reference Cube
for edge in cube_edges:
    ax.plot3D(*zip(corner_centers[edge[0]], corner_centers[edge[1]]),
              color="#7f8c8d", linewidth=1.2, linestyle="--", alpha=0.5, zorder=1)

# 5. Plot Face Disks (Inward Moments)
labeled_f = False
for norm, center in zip(face_normals, face_centers):
    disk = generate_flat_disk(norm, center, r_face_in, r_face_out, color_face)
    ax.add_collection3d(disk)

    disk.set_alpha(0.75)  # 50% transparency

    ax.quiver(center[0], center[1], center[2], -norm[0] * arrow_length, -norm[1] * arrow_length,
              -norm[2] * arrow_length,
              color=color_face, linewidth=2.5, arrow_length_ratio=0.3, zorder=5,
              label="Face Disks (- Inward)" if not labeled_f else "")
    labeled_f = True

# 6. Plot Corner Disks (Outward Moments)
labeled_c = False
for norm, center in zip(corner_normals, corner_centers):
    disk = generate_flat_disk(norm, center, r_corner_in, r_corner_out, color_corner)
    ax.add_collection3d(disk)

    disk.set_alpha(0.5)  # 50% transparency

    ax.quiver(center[0], center[1], center[2], norm[0] * arrow_length, norm[1] * arrow_length, norm[2] * arrow_length,
              color=color_corner, linewidth=2.0, arrow_length_ratio=0.3, zorder=5,
              label="Corner Disks (+ Outward)" if not labeled_c else "")
    labeled_c = True

    ax.plot3D([0, center[0]], [0, center[1]], [0, center[2]],
              color=color_corner, linewidth=0.5, linestyle=":", alpha=0.2, zorder=2)

# Highlight core null point (B = 0)
ax.scatter3D(0, 0, 0, color="gold", s=200, edgecolors='black', label="Isotropic B = 0 Core Well", zorder=10)

# 7. Formatting and Bounds
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('14-Coil Polywell Grid with Flat Uniform Annular Disks', fontsize=13, pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.15, 0.85))

max_val = (d_corner + r_corner_out + 0.2)
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=22, azim=45)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()

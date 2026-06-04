import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- CONFIGURATION ---
radius = 0.22
distance = 1.5  # Distance from center to coil planes

# 1. Generate Base Icosahedron Vertices ( Golden Ratio Framework )
phi = (1.0 + np.sqrt(5.0)) / 2.0
ico_vertices = np.array([
    [1.0, phi, 0.0], [1.0, -phi, 0.0], [-1.0, phi, 0.0], [-1.0, -phi, 0.0],
    [0.0, 1.0, phi], [0.0, 1.0, -phi], [0.0, -1.0, phi], [0.0, -1.0, -phi],
    [phi, 0.0, 1.0], [phi, 0.0, -1.0], [-phi, 0.0, 1.0], [-phi, 0.0, -1.0]
])
# Normalize to get the 12 Pentagon Face Center Directions
pentagon_normals = np.array([v / np.linalg.norm(v) for v in ico_vertices])

# Corrected 20 Triangular Faces of a regular icosahedron
# (Guarantees perfect, symmetrical spacing for the 20 hexagon centroids)
ico_faces = [
    [0, 2, 4], [0, 4, 8], [0, 8, 9], [0, 9, 5], [0, 5, 2], # Top cap around Vertex 0
    [1, 3, 7], [1, 7, 6], [1, 6, 8], [1, 8, 9], [1, 9, 7], # Bottom cap around Vertex 1
    [2, 10, 4], [4, 10, 8], [8, 6, 4], [6, 3, 8], [3, 7, 6], # Middle interlaced band
    [7, 11, 3], [11, 10, 3], [10, 11, 2], [11, 5, 2], [5, 9, 7]
]

hexagon_normals = []
for face in ico_faces:
    vec = np.mean(pentagon_normals[face], axis=0)
    hexagon_normals.append(vec / np.linalg.norm(vec))
hexagon_normals = np.array(hexagon_normals)


def generate_coil_circle(normal, center, radius, num_points=60):
    n = normal / np.linalg.norm(normal)
    not_n = np.array([1, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(n, not_n)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)

    theta = np.linspace(0, 2 * np.pi, num_points)
    circle_points = np.zeros((num_points, 3))
    for j in range(num_points):
        circle_points[j] = center + radius * np.cos(theta[j]) * u + radius * np.sin(theta[j]) * v
    return circle_points


# 3. Setup Plotting Canvas
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

arrow_length = 0.35
color_pentagon = "#3498db"  # Blue for Outward (+)
color_hexagon = "#9b59b6"  # Purple for Inward (-)

# 4. Plot the 12 Pentagon Coils (Polarity: + / Outward)
labeled_p = False
for norm in pentagon_normals:
    center = norm * distance
    coil = generate_coil_circle(normal=norm, center=center, radius=radius)
    ax.plot3D(coil[:, 0], coil[:, 1], coil[:, 2], color=color_pentagon, linewidth=2)
    ax.scatter3D(*center, color=color_pentagon, s=20)

    # Corrected scoping logic: using standard 'not labeled_p'
    ax.quiver(center[0], center[1], center[2], norm[0] * arrow_length, norm[1] * arrow_length, norm[2] * arrow_length,
              color=color_pentagon, linewidth=1.8, arrow_length_ratio=0.3,
              label="Pentagon Coil (+ Outward)" if not labeled_p else "")
    labeled_p = True

# 5. Plot the 20 Hexagon Coils (Polarity: - / Inward)
labeled_h = False
for norm in hexagon_normals:
    center = norm * distance
    coil = generate_coil_circle(normal=norm, center=center, radius=radius)
    ax.plot3D(coil[:, 0], coil[:, 1], coil[:, 2], color=color_hexagon, linewidth=2)
    ax.scatter3D(*center, color=color_hexagon, s=20)

    # Corrected scoping logic: using standard 'not labeled_h'
    ax.quiver(center[0], center[1], center[2], -norm[0] * arrow_length, -norm[1] * arrow_length,
              -norm[2] * arrow_length,
              color=color_hexagon, linewidth=1.8, arrow_length_ratio=0.3,
              label="Hexagon Coil (- Inward)" if not labeled_h else "")
    labeled_h = True

# Highlight central symmetric field null point (B = 0)
ax.scatter3D(0, 0, 0, color="gold", s=180, edgecolors='black', label="True B = 0 Core Well", zorder=10)

# 6. Formatting and Aspect Bounds
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('32-Coil Truncated Icosahedron Configuration (Alternating Multipole)', fontsize=13, pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.15, 0.85))

max_val = (distance + radius + 0.2)
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=20, azim=45)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Draws diagonals inside cube
# --- GEOMETRY CONFIGURATION ---
# To elongate, change z_scale from 1.0.
# As derived, z_scale = 1.0 yields perfect 90-degree projections on XZ, YZ, and XY planes.
z_scale = 1.0
x_scale = 1.0
y_scale = 1.0

vertices = np.array([
    [x_scale, y_scale, z_scale],  # 0
    [x_scale, y_scale, -z_scale],  # 1
    [x_scale, -y_scale, z_scale],  # 2
    [x_scale, -y_scale, -z_scale],  # 3
    [-x_scale, y_scale, z_scale],  # 4
    [-x_scale, y_scale, -z_scale],  # 5
    [-x_scale, -y_scale, z_scale],  # 6
    [-x_scale, -y_scale, -z_scale]  # 7
])

edges = [
    (0, 1), (1, 3), (3, 2), (2, 0),  # Front face
    (4, 5), (5, 7), (7, 6), (6, 4),  # Back face
    (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting edges
]

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# Draw elongated hexahedron wireframe
for edge in edges:
    ax.plot3D(*zip(vertices[edge[0]], vertices[edge[1]]),
              color="black", linewidth=1.0, linestyle="--", alpha=0.5)

# Plot the 8 coil axes
origin = np.array([0, 0, 0])
colors = ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6"]
labels = ["Coil Pair 1", "Coil Pair 2", "Coil Pair 3", "Coil Pair 4"]

for i in range(4):
    v1 = vertices[i]
    v2 = vertices[7 - i]  # Inverted pair

    # Forward ray
    ax.plot3D([origin[0], v1[0]], [origin[1], v1[1]], [origin[2], v1[2]],
              color=colors[i], linewidth=2.5, label=labels[i])
    ax.scatter3D(*v1, color=colors[i], s=40, edgecolors='black')

    # Reverse ray
    ax.plot3D([origin[0], v2[0]], [origin[1], v2[1]], [origin[2], v2[2]],
              color=colors[i], linewidth=2.5)
    ax.scatter3D(*v2, color=colors[i], s=40, edgecolors='black')

ax.scatter3D(0, 0, 0, color="black", s=80, zorder=10)

# Labels and Bounds
ax.set_xlabel('X Axis (Normal to YZ Plane)')
ax.set_ylabel('Y Axis (Normal to XZ Plane)')
ax.set_zlabel('Z Axis (Normal to XY Plane)')
ax.set_title(f'Hexahedron Coil Projections (Z-Scale: {z_scale})', fontsize=12, pad=20)
ax.legend(loc="upper right")

# Dynamic bounding box to maintain aspect ratio integrity
max_val = max(x_scale, y_scale, z_scale) * 1.3
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

# --- VIEWING INSTRUCTION ---
# To visually verify the 90-degree orthographic projections:
# For XY Plane projection: set elev=90, azim=0
# For XZ Plane projection: set elev=0,  azim=-90
# For YZ Plane projection: set elev=0,  azim=0
ax.view_init(elev=20, azim=45)
ax.grid(True, linestyle=':', alpha=0.4)

plt.show()
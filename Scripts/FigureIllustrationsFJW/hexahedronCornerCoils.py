import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- CONFIGURATION ---
radius = 0.5
c = 1.0  # Cube half-width

# 1. Define the 8 vertices of the regular hexahedron (cube)
vertices = np.array([
    [c, c, c],  # 0: +++
    [c, c, -c],  # 1: ++-
    [c, -c, c],  # 2: +-+
    [c, -c, -c],  # 3: +--
    [-c, c, c],  # 4: -++
    [-c, c, -c],  # 5: -+-
    [-c, -c, c],  # 6: --+
    [-c, -c, -c]  # 7: ---
])

edges = [
    (0, 1), (1, 3), (3, 2), (2, 0),  # Front face
    (4, 5), (5, 7), (7, 6), (6, 4),  # Back face
    (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting edges
]


# 2. Function to generate a 3D circle perpendicular to a normal vector
def generate_coil_circle(normal, center, radius, num_points=100):
    n = normal / np.linalg.norm(normal)
    # Find a vector not parallel to n to establish a local coordinate frame
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
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# 4. Draw Hexahedron Wireframe Cage
for edge in edges:
    ax.plot3D(*zip(vertices[edge[0]], vertices[edge[1]]),
              color="#bdc3c7", linewidth=1.0, linestyle="--", alpha=0.5)

# 5. Plot Coils paired by Diagonal Axis
origin = np.array([0, 0, 0])

# 4 unique colors for the 4 distinct diagonal lines of the cube
diagonal_colors = ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6"]  # Red, Blue, Green, Purple
axis_labels = ["Diagonal Axis A", "Diagonal Axis B", "Diagonal Axis C", "Diagonal Axis D"]

# Loop through the first 4 vertices and map them alongside their inverse counterparts
for i in range(4):
    v1 = vertices[i]
    v2 = vertices[7 - i]  # Spatial inversion (opposite end of the long diagonal)
    color = diagonal_colors[i]

    # --- Coil 1 (End 1) ---
    # Axis Ray to vertex 1
    ax.plot3D([origin[0], v1[0]], [origin[1], v1[1]], [origin[2], v1[2]],
              color=color, linewidth=1.2, linestyle=":", alpha=0.6)
    # Coil 1 loop
    coil1 = generate_coil_circle(normal=v1, center=v1, radius=radius)
    ax.plot3D(coil1[:, 0], coil1[:, 1], coil1[:, 2], color=color, linewidth=2.5, label=axis_labels[i])
    ax.scatter3D(*v1, color=color, s=30, edgecolors='black')

    # --- Coil 2 (End 2 - Facing End 1) ---
    # Axis Ray to vertex 2
    ax.plot3D([origin[0], v2[0]], [origin[1], v2[1]], [origin[2], v2[2]],
              color=color, linewidth=1.2, linestyle=":", alpha=0.6)
    # Coil 2 loop (shares the same color)
    coil2 = generate_coil_circle(normal=v2, center=v2, radius=radius)
    ax.plot3D(coil2[:, 0], coil2[:, 1], coil2[:, 2], color=color, linewidth=2.5)
    ax.scatter3D(*v2, color=color, s=30, edgecolors='black')

# Plot core origin
ax.scatter3D(0, 0, 0, color="black", s=60, zorder=10)

# Aspect Ratio and Bounding Box Tuning
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('8 Hexahedron Coils Paired Symmetrically Along Diagonals', fontsize=13, pad=20)
ax.legend(loc="upper right")

max_val = (c + radius) * 1.1
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=22, azim=45)
ax.grid(True, linestyle=':', alpha=0.4)

plt.show()
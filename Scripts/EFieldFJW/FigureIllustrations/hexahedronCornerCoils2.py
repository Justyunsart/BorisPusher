import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- CONFIGURATION ---
radius = 0.4
c = 1.0  # Cube half-width

# 1. Define the 8 vertices of the cube
vertices = np.array([
    [c, c, c],  # 0
    [c, c, -c],  # 1
    [c, -c, c],  # 2
    [c, -c, -c],  # 3
    [-c, c, c],  # 4
    [-c, c, -c],  # 5
    [-c, -c, c],  # 6
    [-c, -c, -c]  # 7
])

edges = [
    (0, 1), (1, 3), (3, 2), (2, 0),  # Front face
    (4, 5), (5, 7), (7, 6), (6, 4),  # Back face
    (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting edges
]


def generate_coil_circle(normal, center, radius, num_points=100):
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
fig = plt.figure(figsize=(11, 11))
ax = fig.add_subplot(111, projection='3d')

# 4. Draw Hexahedron Wireframe Cage
for edge in edges:
    ax.plot3D(*zip(vertices[edge[0]], vertices[edge[1]]),
              color="black", linewidth=1.0, linestyle="--", alpha=0.5)

# 5. Plot Coils and Magnetic Moment Quivers
# Custom color coding: Crimson for Outward (+), Dark Blue for Inward (-)
color_out = "#3498db"
color_in = "#2ecc71"
labeled_out = False
labeled_in = False
labeled_out = False
labeled_in = False
color_in = "#2ecc71"

labeled_out = False
labeled_in = False

for i in range(8):
    v = vertices[i]

    # Determine adjacent alternating sign via coordinate product
    sign_product = np.prod(v)

    # Define unit normal pointing outward from origin
    unit_normal = v / np.linalg.norm(v)

    if sign_product > 0:
        # Positive Current -> Moment points OUTWARD (away from origin)
        color = color_out
        direction = unit_normal
        label = "Moment Outward (+)" if not labeled_out else ""
        labeled_out = True
    else:
        # Negative Current -> Moment points INWARD (toward origin)
        color = color_in
        direction = -unit_normal
        label = "Moment Inward (-)" if not labeled_in else ""
        labeled_in = True

    # Plot the coil loop at the vertex
    coil = generate_coil_circle(normal=v, center=v, radius=radius)
    ax.plot3D(coil[:, 0], coil[:, 1], coil[:, 2], color=color, linewidth=2.5)
    ax.scatter3D(*v, color=color, s=30, edgecolors='black', zorder=4)

    # Draw Magnetic Moment Vector Arrow emanating from the coil center
    # Arrow length scaled for clear visibility relative to loop size
    arrow_length = 0.5
    ax.quiver(v[0], v[1], v[2],
              direction[0] * arrow_length, direction[1] * arrow_length, direction[2] * arrow_length,
              color=color, linewidth=2.5, arrow_length_ratio=0.3, label=label)

# Plot core origin
ax.scatter3D(0, 0, 0, color="black", s=60, zorder=10)

# Aspect Ratio and Bounding Box Tuning
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('Alternating Multipole Configuration: Magnetic Moment Vectors', fontsize=13, pad=20)
ax.legend(loc="upper right")

max_val = (c + radius + 0.3) * 1.1
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=22, azim=45)
ax.grid(True, linestyle=':', alpha=0.4)

plt.show()
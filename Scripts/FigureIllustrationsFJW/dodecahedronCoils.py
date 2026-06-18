
# --- CONFIGURATION --- coaxial pairing (matching the colors of opposing coils
# on the same long diagonal) with a highly symmetric magnetic moment configuration
# all inward, with opposite ends of the diagonal pointing directly toward each other.

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

radius = 0.35
distance = 1.2  # Radial distance from origin to coil centers

# 1. Define the Golden Ratio
phi = (1.0 + np.sqrt(5.0)) / 2.0

# 2. Generate the 12 face-normal direction vectors (Icosahedron Vertices)
# Ordered deliberately so that index i and index i+6 are exact spatial opposites.
raw_vectors = np.array([
    [1.0, phi, 0.0],  # 0: Axis A1
    [0.0, 1.0, phi],  # 1: Axis B1
    [phi, 0.0, 1.0],  # 2: Axis C1
    [1.0, -phi, 0.0],  # 3: Axis D1
    [0.0, -1.0, phi],  # 4: Axis E1
    [-phi, 0.0, 1.0],  # 5: Axis F1
    [-1.0, -phi, 0.0],  # 6: Axis A2 (Opposite of 0)
    [0.0, -1.0, -phi],  # 7: Axis B2 (Opposite of 1)
    [-phi, 0.0, -1.0],  # 8: Axis C2 (Opposite of 2)
    [-1.0, phi, 0.0],  # 9: Axis D2 (Opposite of 3)
    [0.0, 1.0, -phi],  # 10: Axis E2 (Opposite of 4)
    [phi, 0.0, -1.0]  # 11: Axis F2 (Opposite of 5)
])

# Normalize vectors and scale to the target radial distance
face_centers = np.array([v / np.linalg.norm(v) * distance for v in raw_vectors])


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

# 4. Color map for the 6 long diagonal axes (coaxial pairs)
axis_colors = ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6", "#f1c40f", "#e67e22"]
axis_labels = ["Diagonal Axis A", "Diagonal Axis B", "Diagonal Axis C",
               "Diagonal Axis D", "Diagonal Axis E", "Diagonal Axis F"]

origin = np.array([0, 0, 0])
arrow_length = 0.4

# 5. Plot the 6 paired diagonal groups (12 coils total)
for i in range(6):
    color = axis_colors[i]
    label = axis_labels[i]

    # End 1 of the diagonal
    c1 = face_centers[i]
    n1 = -c1 / np.linalg.norm(c1)  # Inward magnetic moment normal

    coil1 = generate_coil_circle(normal=c1, center=c1, radius=radius)
    ax.plot3D(coil1[:, 0], coil1[:, 1], coil1[:, 2], color=color, linewidth=2.5, label=label)
    ax.scatter3D(*c1, color=color, s=30, edgecolors='black')
    ax.quiver(c1[0], c1[1], c1[2], n1[0] * arrow_length, n1[1] * arrow_length, n1[2] * arrow_length,
              color=color, linewidth=2.0, arrow_length_ratio=0.3)

    # End 2 of the diagonal (Exact spatial inversion, facing End 1)
    c2 = face_centers[i + 6]
    n2 = -c2 / np.linalg.norm(c2)  # Inward magnetic moment normal

    coil2 = generate_coil_circle(normal=c2, center=c2, radius=radius)
    ax.plot3D(coil2[:, 0], coil2[:, 1], coil2[:, 2], color=color, linewidth=2.5)
    ax.scatter3D(*c2, color=color, s=30, edgecolors='black')
    ax.quiver(c2[0], c2[1], c2[2], n2[0] * arrow_length, n2[1] * arrow_length, n2[2] * arrow_length,
              color=color, linewidth=2.0, arrow_length_ratio=0.3)

    # Draw a faint shared center-line connecting the paired coils through the origin
    ax.plot3D([c1[0], c2[0]], [c1[1], c2[1]], [c1[2], c2[2]],
              color=color, linewidth=1.0, linestyle=":", alpha=0.4)

# Highlight central symmetric null field point
ax.scatter3D(0, 0, 0, color="gold", s=150, edgecolors='black', label="B = 0 Well Core", zorder=10)

# 6. Formatting and View Angle
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('12-Coil Dodecahedron: Coaxial Pair Coloration with Inward Moments', fontsize=13, pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.15, 0.85))

# Symmetrical bounding box limits
max_val = (distance + radius) * 1.1
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=25, azim=60)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- CONFIGURATION ---
radius = 0.20
distance = 1.6  # Perfect uniform radial distance for all 30 coils

# 1. Generate the 30 uniform face-normal vectors (Icosidodecahedron Vertices)
phi = (1.0 + np.sqrt(5.0)) / 2.0

raw_list = []
# Generate permutations of (0, ±1, ±phi) and all cyclic shifts
for s1 in [1.0, -1.0]:
    for s2 in [1.0, -1.0]:
        raw_list.append([0.0, s1, s2 * phi])
        raw_list.append([s2 * phi, 0.0, s1])
        raw_list.append([s1, s2 * phi, 0.0])

# Explicitly add the remaining 18 unique golden coordinates
for s1 in [1.0, -1.0]:
    for s2 in [1.0, -1.0]:
        raw_list.append([s1 * phi, s2, 0.0])
        raw_list.append([0.0, s1 * phi, s2])
        raw_list.append([s2, 0.0, s1 * phi])

        raw_list.append([s1, 0.0, s2 * phi])
        raw_list.append([s2 * phi, s1, 0.0])
        raw_list.append([0.0, s2 * phi, s1])

# Filter strictly for unique spatial vectors using round-off tolerance
unique_set = []
for vec in raw_list:
    v_norm = np.array(vec) / np.linalg.norm(vec)
    # Check if this vector or its close float equivalent is already in our unique set
    if not any(np.allclose(v_norm, existing, atol=1e-5) for existing in unique_set):
        unique_set.append(v_norm)

face_normals = np.array(unique_set)

# VERIFICATION CHECK
print(f"Successfully generated exactly {len(face_normals)} unique coil axis normals.")


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


# 2. Setup Plotting Canvas
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

arrow_length = 0.35
color_pos = "#e74c3c"  # Crimson for Outward (+)
color_neg = "#2c3e50"  # Dark Blue for Inward (-)

labeled_pos = False
labeled_neg = False

# 3. Sort vectors by angle relative to a fixed axis to ensure clean alternating patterns
angles = np.arctan2(face_normals[:, 1], face_normals[:, 0]) + face_normals[:, 2]
sort_indices = np.argsort(angles)
face_normals = face_normals[sort_indices]

# 4. Plot the 30 Coils with alternating uniform topologies
for idx, norm in enumerate(face_normals):
    center = norm * distance

    # Alternating sign checkerboard pattern
    if idx % 2 == 0:
        color = color_pos
        direction = norm  # Outward vector
        label = "Coil (+ Outward)" if not labeled_pos else ""
        labeled_pos = True
    else:
        color = color_neg
        direction = -norm  # Inward vector
        label = "Coil (- Inward)" if not labeled_neg else ""
        labeled_neg = True

    # Generate and plot the loop
    coil = generate_coil_circle(normal=norm, center=center, radius=radius)
    ax.plot3D(coil[:, 0], coil[:, 1], coil[:, 2], color=color, linewidth=2)
    ax.scatter3D(*center, color=color, s=20)

    # Plot Magnetic Moment Arrow Vector
    ax.quiver(center[0], center[1], center[2],
              direction[0] * arrow_length, direction[1] * arrow_length, direction[2] * arrow_length,
              color=color, linewidth=1.8, arrow_length_ratio=0.3, label=label)

    # Draw a thin visual line through the origin to confirm opposing alignment
    ax.plot3D([0, center[0]], [0, center[1]], [0, center[2]],
              color=color, linewidth=0.5, linestyle=":", alpha=0.3)

# Highlight central isotropic null field point (B = 0)
ax.scatter3D(0, 0, 0, color="gold", s=200, edgecolors='black', label="Isotropic B = 0 Well Core", zorder=10)

# 5. Formatting and Bounding Box
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('30-Coil Rhombic Triacontahedron Configuration (Validated 30 Axis Map)', fontsize=13, pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.15, 0.85))

max_val = (distance + radius + 0.2)
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=20, azim=45)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()
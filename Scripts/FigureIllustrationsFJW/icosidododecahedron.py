import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- CONFIGURATION ---
radius = 0.20
distance = 1.6  # Uniform radial distance for all 24 coils

# 1. Generate the 24 uniform vectors (Rhombicuboctahedron Vertices)
alpha = 1.0 + np.sqrt(2.0)
raw_list = []

# Generate all permutations and sign combinations of (±1, ±1, ±alpha)
for s1 in [1.0, -1.0]:
    for s2 in [1.0, -1.0]:
        for s3 in [1.0, -1.0]:
            raw_list.append([s1, s2, s3 * alpha])
            raw_list.append([s3 * alpha, s1, s2])
            raw_list.append([s2, s3 * alpha, s1])

# Filter strictly for unique spatial vectors using an explicit tolerance loop
unique_set = []
for vec in raw_list:
    v_norm = np.array(vec) / np.linalg.norm(vec)
    if not any(np.allclose(v_norm, existing, atol=1e-4) for existing in unique_set):
        unique_set.append(v_norm)

face_normals = np.array(unique_set)
num_coils = len(face_normals)

print(f"Successfully generated exactly {num_coils} unique coil axis normals.")

# 2. Compute the 3D Distance Matrix to find Nearest Neighbors
dist_matrix = np.zeros((num_coils, num_coils))
for i in range(num_coils):
    for j in range(num_coils):
        dist_matrix[i, j] = np.linalg.norm(face_normals[i] - face_normals[j])

# 3. Apply the Coordinate-Parity Rule for Perfect Alternation & Coaxial Pairing
polarities = np.zeros(num_coils, dtype=int)
for i, norm in enumerate(face_normals):
    # Base coordinate sign product
    sign_product = np.sign(norm[0]) * np.sign(norm[1]) * np.sign(norm[2])

    # Identify which component holds the larger 'alpha' value to track structural orientation
    max_axis = np.argmax(np.abs(norm))

    # Combine sign product with axis parity to lock coaxial pairs to the same polarity
    if max_axis == 0:
        polarities[i] = int(sign_product)
    elif max_axis == 1:
        polarities[i] = int(-sign_product)
    else:
        polarities[i] = int(sign_product)

# 4. Programmatic Verification Check
errors = 0
for i in range(num_coils):
    # Nearest neighbors are at a distance of approx 0.55 on a unit sphere
    neighbor_indices = np.where((dist_matrix[i] > 0.1) & (dist_matrix[i] < 0.6))[0]
    for n_idx in neighbor_indices:
        if polarities[i] == polarities[n_idx]:
            errors += 1

print(f"Polarity check complete. Neighbor placement errors: {errors}")
print(f"Total Positive Coils (Outward): {np.sum(polarities == 1)}")
print(f"Total Negative Coils (Inward): {np.sum(polarities == -1)}")


# --- PLOTTING ---
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


fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

arrow_length = 0.35
color_pos = "#e74c3c"  # Crimson for Outward (+)
color_neg = "#2c3e50"  # Dark Blue for Inward (-)

labeled_pos = False
labeled_neg = False

for idx, norm in enumerate(face_normals):
    center = norm * distance
    pol = polarities[idx]

    if pol == 1:
        color = color_pos
        direction = norm
        label = "Coil (+ Outward)" if not labeled_pos else ""
        labeled_pos = True
    else:
        color = color_neg
        direction = -norm
        label = "Coil (- Inward)" if not labeled_neg else ""
        labeled_neg = True

    # Render the circular diagnostic loops
    coil = generate_coil_circle(normal=norm, center=center, radius=radius)
    ax.plot3D(coil[:, 0], coil[:, 1], coil[:, 2], color=color, linewidth=2)
    ax.scatter3D(*center, color=color, s=25, edgecolors='black')

    # Plot Magnetic Moment Vector Arrows
    ax.quiver(center[0], center[1], center[2],
              direction[0] * arrow_length, direction[1] * arrow_length, direction[2] * arrow_length,
              color=color, linewidth=2.0, arrow_length_ratio=0.3, label=label)

    # Draw radial lines to confirm coaxial alignment through the origin
    ax.plot3D([0, center[0]], [0, center[1]], [0, center[2]],
              color=color, linewidth=0.5, linestyle=":", alpha=0.2)

# Central absolute field null
ax.scatter3D(0, 0, 0, color="gold", s=200, edgecolors='black', label="Isotropic B = 0 Well Core", zorder=10)

ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('24-Coil Rhombicuboctahedron Polywell\n(Balanced 12/12 Alternating Multipole Lattice)', fontsize=13,
             pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.15, 0.85))

max_val = (distance + radius + 0.2)
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_zlim(-max_val, max_val)

ax.view_init(elev=20, azim=45)
ax.grid(True, linestyle=':', alpha=0.3)

plt.show()
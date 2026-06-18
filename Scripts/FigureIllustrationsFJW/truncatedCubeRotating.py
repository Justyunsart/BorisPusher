"""
Rotating truncated cube, transparent faces.
FJW 6.18.26
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 1. Define Vertices of a Truncated Cube
# xi = np.sqrt(2) - 1  # ~0.414
xi = 0.2  # ~0.414

# Generate all unique permutations and sign combinations
base_coords = [
    (xi, 1, 1), (1, xi, 1), (1, 1, xi)
]

vertices = []
for coord in base_coords:
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                vertices.append([coord[0] * sx, coord[1] * sy, coord[2] * sz])

# Remove duplicates and convert to unique numpy array
vertices = np.unique(np.array(vertices), axis=0)

# 2. Define Faces by grouping vertices that share planes
# There are 6 octagons (x=±1, y=±1, z=±1) and 8 triangles (cutting the corners)
faces = []
face_colors = []

# Find the 6 Octagons (where one coordinate is fixed at 1 or -1)
for dim in range(3):
    for val in [-1, 1]:
        # Gather all vertices lying on this plane
        idx = np.where(np.isclose(vertices[:, dim], val))[0]
        pts = vertices[idx]

        # Sort vertices cyclically to form a proper polygon around the face center
        center = np.mean(pts, axis=0)
        other_dims = [d for d in range(3) if d != dim]
        angles = np.arctan2(pts[:, other_dims[1]] - center[other_dims[1]],
                            pts[:, other_dims[0]] - center[other_dims[0]])
        sorted_idx = idx[np.argsort(angles)]

        faces.append(vertices[sorted_idx])
        face_colors.append('#3498db')  # Blue for octagons

# Find the 8 Triangles (by identifying remaining open corner sets)
# Triangles connect the 3 truncated points around each of the 8 original cube corners
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            # Find the 3 vertices closest to this original cube corner
            dist = np.sum((vertices - np.array([sx, sy, sz])) ** 2, axis=1)
            closest_idx = np.argsort(dist)[:3]
            faces.append(vertices[closest_idx])
            face_colors.append('#e74c3c')  # Red/Orange for triangles

# 3. Setup the 3D Plot
fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection='3d')

# Set aesthetic limits and remove axes background for a clean look
ax.set_xlim([-1.2, 1.2])
ax.set_ylim([-1.2, 1.2])
ax.set_zlim([-1.2, 1.2])
ax.axis('off')

# Initialize the 3D Poly3DCollection
# poly_collection = Poly3DCollection(faces, facecolors=face_colors, edgecolors='black', linewidths=1.5, alpha=0.85)
poly_collection = Poly3DCollection(
    faces,
    facecolors='lightgray',
    edgecolors='dimgray',  # Matrix green lines
    linewidths=1.8,
    shade=True,
    alpha=0.85
)
ax.add_collection3d(poly_collection)


# 4. Animation Function
def update(frame):
    # Rotate view angle dynamically over time
    ax.view_init(elev=20 + 10 * np.sin(frame * 0.02), azim=frame * 0.5)
    return poly_collection,


# Create the continuous rotation animation
ani = FuncAnimation(fig, update, frames=720, interval=20, blit=False)

plt.show()
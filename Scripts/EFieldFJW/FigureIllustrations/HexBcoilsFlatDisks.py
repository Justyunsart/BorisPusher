"""
3-D Hexahedron Solid Disk Coil Visualizer
Generates 6 solid annular disks positioned on the faces of a cube
using an enhanced high-visibility colormap gradient.

Author: Adapted for FJ Wessel workflow layout
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# ============================================================
# Global Parameters
# ============================================================
# a = 0.48       # Inner radius (m)
a = 0.15      # Inner radius (m)
# b = 0.52       # Outer radius (m)
b = 0.85       # Outer radius (m)
L = 1.0        # Offset distance from origin to each face center


# ============================================================
# Rotation Utilities for 3D Space
# ============================================================

def rotation_matrix_from_vectors(vec1, vec2):
    """Returns a rotation matrix that maps vec1 to vec2."""
    a_vec = vec1 / np.linalg.norm(vec1)
    b_vec = vec2 / np.linalg.norm(vec2)
    v = np.cross(a_vec, b_vec)
    c = np.dot(a_vec, b_vec)
    if np.isclose(c, 1):
        return np.eye(3)
    if np.isclose(c, -1):
        axis = np.array([1, 0, 0]) if not np.allclose(a_vec, [1, 0, 0]) else np.array([0, 1, 0])
        return rotation_matrix_axis_angle(axis, np.pi)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / s ** 2)


def rotation_matrix_axis_angle(axis, angle):
    """Returns a rotation matrix around a given axis by a specific angle."""
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1 - c
    return np.array([
        [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, c + z * z * C]
    ])


# ============================================================
# 3D Solid Disk Mesh Generation
# ============================================================

def plot_3d_solid_disk(ax, center, normal, a_rad, b_rad, colormap_name='plasma', flat_color=None, r_pts=30, theta_pts=100):
    """
    Generates a 2D coordinate mesh for an annular disk, rotates/translates it,
    and plots it as a solid 3D surface object with custom coloring.
    """
    # Create a 2D grid for radius (a to b) and angle (0 to 2pi)
    r_vals = np.linspace(a_rad, b_rad, r_pts)
    theta_vals = np.linspace(0, 2 * np.pi, theta_pts)
    R_mesh, Theta_mesh = np.meshgrid(r_vals, theta_vals)

    # Generate flat unrotated local coordinates in the XY plane
    X_local = R_mesh * np.cos(Theta_mesh)
    Y_local = R_mesh * np.sin(Theta_mesh)
    Z_local = np.zeros_like(X_local)

    # Flatten the mesh to easily apply the 3D rotation matrix
    orig_shape = X_local.shape
    local_pts = np.vstack((X_local.flatten(), Y_local.flatten(), Z_local.flatten())).T

    # Get rotation matrix from local flat z-normal [0,0,1] to the target face normal
    Rot = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))

    # Rotate and translate all grid points globally
    global_pts = (Rot @ local_pts.T).T + np.array(center)

    # Reshape back into a 2D structure compatible with plot_surface
    X_global = global_pts[:, 0].reshape(orig_shape)
    Y_global = global_pts[:, 1].reshape(orig_shape)
    Z_global = global_pts[:, 2].reshape(orig_shape)

    # Handle color options
    if flat_color is not None:
        # Uniform solid color style
        ax.plot_surface(
            X_global, Y_global, Z_global,
            color=flat_color,
            alpha=0.95,           # Increased visibility/opacity
            shade=True,
            linewidth=0,
            antialiased=True
        )
    else:
        # Radial gradient colormap style
        norm = plt.Normalize(vmin=a_rad, vmax=b_rad)
        cmap = plt.get_cmap(colormap_name)
        facecolors = cmap(norm(R_mesh))

        ax.plot_surface(
            X_global, Y_global, Z_global,
            facecolors=facecolors,
            alpha=0.95,  # Keeps the layout highly opaque
            shade=False,  # Keeps the colors bright instead of shadowy
            linewidth=0,  # <-- CHANGE THIS TO 0 (Removes the line thickness)
            edgecolor='none',  # <-- CHANGE THIS TO 'none' (Removes the black borders)
            antialiased=True
        )


# ============================================================
# Main Script / Plotting
# ============================================================

if __name__ == "__main__":

    # Hexahedron faces definitions: Using 'plasma' for supreme vibrant contrast
    face_definitions = [
        ([L, 0, 0], [1, 0, 0], 'inferno'),       # +X Face
        ([-L, 0, 0], [-1, 0, 0], 'inferno'),     # -X Face
        ([0, L, 0], [0, 1, 0], 'inferno'),       # +Y Face
        ([0, -L, 0], [0, -1, 0], 'inferno'),     # -Y Face
        ([0, 0, L], [0, 0, 1], 'inferno'),       # +Z Face
        ([0, 0, -L], [0, 0, -1], 'inferno'),      # -Z Face
    ]

    # Initialize 3D plotting canvas
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Loop over all 6 faces of the hexahedron and render them as solid surfaces
    for center, normal, cmap_choice in face_definitions:
        plot_3d_solid_disk(ax, center, normal, a, b, colormap_name=cmap_choice)

    # ============================================================
    # Aesthetics & Boundary Configuration
    # ============================================================

    # Draw a reference bounding box framework around the hexahedron structure
    r_box = [-L, L]
    for s, e in [([s, y, z], [e, y, z]) for s in r_box for e in r_box for y in r_box for z in r_box if s != e] + \
               [([x, s, z], [x, e, z]) for x in r_box for s in r_box for e in r_box for z in r_box if s != e] + \
               [([x, y, s], [x, y, e]) for x in r_box for y in r_box for s in r_box for e in r_box if s != e]:
        ax.plot3D(*zip(s, e), color="black", linestyle=":", linewidth=0.8, alpha=0.3)

    # Set spatial axes constraints
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])

    ax.set_xlabel("X (m)", fontsize=11, labelpad=10)
    ax.set_ylabel("Y (m)", fontsize=11, labelpad=10)
    ax.set_zlabel("Z (m)", fontsize=11, labelpad=10)

    ax.set_title(
        f"Hexahedral, Face Mounted Magnet Coils\n"
        f"Offset $L$ = {L} m, Inner & Outer Radii $a$ = {a} m, $b$ = {b} m",
        fontsize=14,
        pad=20
    )

    # Optimize aspect ratio to avoid distortion of the geometric shapes
    ax.set_aspect('equal')

    # Set default camera view for clean perspective visibility across all axes
    ax.view_init(elev=25, azim=45)

    plt.show()
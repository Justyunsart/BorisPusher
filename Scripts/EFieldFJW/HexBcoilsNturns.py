"""
3-D Hexahedron Coil Configuration Visualizer
Generates 6 multi-turn annular disk coils positioned on the faces of a cube.

Author: Adapted for FJ Wessel workflow layout
"""

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO


# ============================================================
# Rotation Utilities for 3D Space
# ============================================================

def rotation_matrix_from_vectors(vec1, vec2):
    """Returns a rotation matrix that maps vec1 to vec2."""
    a = vec1 / np.linalg.norm(vec1)
    b = vec2 / np.linalg.norm(vec2)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.isclose(c, 1):
        return np.eye(3)
    if np.isclose(c, -1):
        axis = np.array([1, 0, 0]) if not np.allclose(a, [1, 0, 0]) else np.array([0, 1, 0])
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
# 3D Coil Generation
# ============================================================

def generate_3d_disk_coil(center, normal, a, b, turns=10, pts_per_turn=100):
    """
    Generates the 3D coordinates for a multi-turn annular disk coil.
    Returns a list of 3D lines (arrays of shape [pts, 3]).
    """
    # 1. Generate concentric radii from inner radius 'a' to outer radius 'b'
    radii = np.linspace(a, b, turns)
    theta = np.linspace(0, 2 * np.pi, pts_per_turn)

    # Get rotation matrix from local flat z-normal [0,0,1] to the target face normal
    R = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))

    coil_filaments = []
    for r in radii:
        # Local coordinates in the XY plane before tilting
        x_local = r * np.cos(theta)
        y_local = r * np.sin(theta)
        z_local = np.zeros_like(theta)

        local_pts = np.vstack((x_local, y_local, z_local)).T  # Shape: [pts_per_turn, 3]

        # Rotate to match face normal and translate to the face center
        global_pts = (R @ local_pts.T).T + np.array(center)
        coil_filaments.append(global_pts)

    return coil_filaments


# ============================================================
# Main Script / Plotting
# ============================================================

if __name__ == "__main__":
    # Given problem parameters
    a = 0.1  # Inner radius (m)
    b = 0.9  # Outer radius (m)
    offset = 1.0  # Distance from origin to each face center
    turns = 10  # Number of concentric wire loops per face disk

    # Hexahedron faces definitions: (Center Position, Normal Vector, Color Scheme)
    face_definitions = [
        ([offset, 0, 0], [1, 0, 0], 'navy'),  # +X Face
        ([-offset, 0, 0], [-1, 0, 0], 'navy'),  # -X Face
        ([0, offset, 0], [0, 1, 0], 'navy'),  # +Y Face
        ([0, -offset, 0], [0, -1, 0], 'navy'),  # -Y Face
        ([0, 0, offset], [0, 0, 1], 'navy'),  # +Z Face
        ([0, 0, -offset], [0, 0, -1], 'navy'),  # -Z Face
    ]

    # Initialize 3D plotting canvas
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Loop over all 6 faces of the hexahedron and generate/plot the coils
    for center, normal, color in face_definitions:
        filaments = generate_3d_disk_coil(center, normal, a, b, turns=turns)

        # Plot each turn/filament of the active disk coil
        for i, filament in enumerate(filaments):
            # Give the outer/inner limits a slightly thicker line weight for a cleaner aesthetic
            lw = 2.0 if (i == 0 or i == turns - 1) else 0.8
            alpha = 1.0 if (i == 0 or i == turns - 1) else 0.6

            ax.plot(
                filament[:, 0],
                filament[:, 1],
                filament[:, 2],
                color=color,
                linewidth=lw,
                alpha=alpha
            )

    # ============================================================
    # Aesthetics & Boundary Configuration
    # ============================================================

    # Draw reference box tracking the outer limits of the hexahedron frame
    r_box = [-offset, offset]
    for s, e in [([s, y, z], [e, y, z]) for s in r_box for e in r_box for y in r_box for z in r_box if s != e] + \
                [([x, s, z], [x, e, z]) for x in r_box for s in r_box for e in r_box for z in r_box if s != e] + \
                [([x, y, s], [x, y, e]) for x in r_box for y in r_box for s in r_box for e in r_box if s != e]:
        ax.plot3D(*zip(s, e), color="black", linestyle=":", linewidth=0.8, alpha=0.4)

    # Set spatial axes constraints
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])

    ax.set_xlabel("X (m)", fontsize=11, labelpad=10)
    ax.set_ylabel("Y (m)", fontsize=11, labelpad=10)
    ax.set_zlabel("Z (m)", fontsize=11, labelpad=10)

    ax.set_title(
        f"3D Hexahedron Face Coils\n"
        f"Inner Radius $a$ = {a}m, Outer Radius $b$ = {b}m",
        fontsize=14,
        pad=20
    )

    # Optimize aspect ratio to avoid distortion of the spheres/circles
    ax.set_aspect('equal')

    # Set default camera view for clean perspective visibility across all axes
    ax.view_init(elev=25, azim=45)

    plt.show()
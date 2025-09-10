import numpy as np
from matplotlib.patches import Wedge
import matplotlib as mpl
import matplotlib.pyplot as plt


# Washer parameters
Q = 1e-11
a, b = 0.25, 0.75
sigma = Q / (np.pi * (b**2 - a**2))
disk_separation = 2.0
offset = disk_separation / 2
# Integration grid for radius
R = np.linspace(a, b, 150)

plt.figure(figsize=(10, 8))
ax = plt.gca()

# Function to draw annular region (washer)
def draw_xy_washer_cross_section(z_positions, color='purple', alpha=0.4):
    """Draw shaded annular disks in the x-y plane intersecting the xz-plane at given z positions."""
    for z in z_positions:
        # Draw a ring centered at (x=0, z)
        ring = Wedge(center=(0, z), r=b, theta1=0, theta2=360, width=b - a,
                     facecolor=color, edgecolor='k', alpha=alpha)
        ax.add_patch(ring)

# Draw shaded annular disks intersecting the xz-plane
draw_xy_washer_cross_section(z_positions=[-offset, offset], color='purple', alpha=0.4)

# draw_xy_washer_cross_section(center=(0, 0), orientation='z', color='green', alpha=0.4)  # ±z-axis
# draw_xy_washer_cross_section(center=(0, 0), orientation='x', color='blue', alpha=0.4)   # ±x-axis

plt.axis('equal')
plt.xlim(-1.5, 1.5)
plt.ylim(-1.5, 1.5)
plt.xlabel('x (m)')
plt.ylabel('z (m)')
plt.title("Electric Field Streamlines from 6 Inward-Facing Annular Disks (xz-plane)")
plt.grid(True)
plt.show()

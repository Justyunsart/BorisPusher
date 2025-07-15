import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Rotation matrices
def Rx(theta):
    return np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])

def Ry(theta):
    return np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

# Initial unit vector along z-axis
v0 = np.array([0, 0, 1])

# Rotation angle
thetaX = np.radians(35)
thetaXdeg = np.degrees(thetaX)
thetaY = np.radians(45)
thetaYdeg = np.degrees(thetaY)

# Apply rotations
v1 = Rx(thetaX) @ v0              # After rotation about x-axis
v2 = Ry(thetaY) @ v1              # After subsequent rotation about y-axis

# 3D Visualization
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Axes
ax.quiver(0, 0, 0, 1, 0, 0, color='b')
ax.quiver(0, 0, 0, 0, 1, 0, color='b')
ax.quiver(0, 0, 0, 0, 0, 1, color='b')

# Vectors
ax.quiver(0, 0, 0, *v0, color='gray', linestyle='dashed', linewidth=2.5, label='Original Vector [0 0 1]')
ax.quiver(0, 0, 0, *v1, color='orange', linewidth=2.5, label='X rotation')
ax.quiver(0, 0, 0, *v2, color='magenta', linewidth=2.5, label='X and Y rotations')

# Axes settings
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title(fr'Unit Vector [0 0 1] rotated {thetaXdeg}$^\circ$ about the X axis and {thetaYdeg}$^\circ$ about the Y axis')
ax.legend()
ax.view_init(elev=20, azim=35)
plt.tight_layout()
plt.show()

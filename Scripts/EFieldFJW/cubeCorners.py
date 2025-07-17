"Rotates the unit vector, once about each of the x, y, z axes."
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

def Rz(theta):
    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

# Initial unit vector along z-axis
v0 = np.array([0, 0, 1])

# Rotation angle
thetaX = np.radians(35)
thetaXdeg = np.degrees(thetaX)
thetaY = np.radians(45)
thetaYdeg = np.degrees(thetaY)
thetaZ = np.radians(90)
thetaZdeg = np.degrees(thetaY)

# Apply rotations
v1 = Rx(thetaX) @ v0              # After rotation about x-axis
v1mag = np.linalg.norm(v1)        # After rotation about x-axis
v2 = Ry(thetaY) @ v1              # After rotation about y-axis
v2mag = np.linalg.norm(v2)        # After rotation about x-axis
v3 = Rz(thetaZ) @ v2              # After another rotation about y-axis
v4 = Rz(thetaZ) @ v3              # After another rotation about y-axis
v5 = Rz(thetaZ) @ v4              # After another rotation about y-axis

flipZ = Rx(np.pi)  # 180° about x-axis
v6 = -1 * v2
v7 = -1 * v3
v8 = -1 * v4
v9 =  -1 * v5

vectors = [v0, v1, v2, v3, v4, v5, v6, v7, v8, v9]
labels = ['V0 = [0 0 1]',
    'V1 = Rx(35.26) * V0',
    'V2 = Ry(45) * V1',
    'V3 = Rz(90) * V2',
    'V4 = Rz(180) * V2',
    'V5 = Rz(270) * V2',
    'V6 = [-1 -1 -1] * V2',
    'V7 = [-1 -1 -1]  * V3',
    'V8 = [-1 -1 -1]  * V4',
    'V9 = [-1 -1 -1] * V5'
          ]
rainbow_colors = [
    '#404040',  # Dark Grey
    '#B200FF',  # Violet
    '#FF0000',  # Red
    '#FF7F00',  # Orange
    '#00FF00',  # Green
    '#0000FF',  # Blue
    '#FF0000',  # Red
    '#FF7F00',  # Orange
    '#00FF00',  # Green
    '#0000FF'  # Blue
]

# 3D Visualization
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
origin =[0, 0, 0]
xaxis = [0.3, 0, 0]
yaxis = [0, 0.3, 0]
zaxis = [0, 0, 0.3]

# Axes
ax.quiver(*origin, *xaxis, linewidth =4, color='k')
ax.quiver(*origin, *yaxis, linewidth=4, color='k')
ax.quiver(*origin, *zaxis, linewidth=4, color='k')

# Label the end of the vector with "X"
endX = np.array(origin) + np.array(xaxis) + [0.2, 0, 0]
endY = np.array(origin) + np.array(yaxis) + [0, 0.2, 0]
endZ = np.array(origin) + np.array(zaxis) + [0, 0, 0.2]
ax.text(*endX,'X', color='k', fontsize=20, fontweight='bold', ha='center', va='center')
ax.text(*endY,'Y', color='k', fontsize=20, fontweight='bold', ha='center', va='center')
ax.text(*endZ,'Z', color='k', fontsize=20, fontweight='bold', ha='center', va='center')

# Plot Vectors
for vec, label, color in zip(vectors, labels, rainbow_colors):
    ax.quiver(*origin, *vec, color = color, linewidth = 2.5, label = label)

# Axes
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
# ax.set_title(fr'[0 0 1] Unit Vector Rotated in +Z Quadrants to the Cube Corners')
ax.legend()
ax.view_init(elev=20, azim=35)
plt.tight_layout()
plt.show()

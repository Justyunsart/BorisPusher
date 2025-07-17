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
v1mag = np.linalg.norm(v1)              # After rotation about x-axis
v2 = Ry(thetaY) @ v1              # After rotation about y-axis
v2mag = np.linalg.norm(v2)              # After rotation about x-axis
# print(v1, v1mag, v2, v2mag)
v3 = Rz(thetaZ) @ v2              # After another rotation about y-axis
v4 = Rz(thetaZ) @ v3              # After another rotation about y-axis
v5 = Rz(thetaZ) @ v4              # After another rotation about y-axis

flipZ = Rx(np.pi)  # 180° about x-axis
v6 = flipZ @ v2
v7 = flipZ @ v3
v8 = flipZ @ v4
v9 = flipZ @ v5


# 3D Visualization
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
origin =[0, 0, 0]
xaxis = [0.5, 0, 0]
yaxis = [0, 0.5, 0]
zaxis = [0, 0, 0.5]

# Axes
ax.quiver(*origin, *xaxis, linewidth =4, color='k')
ax.quiver(*origin, *yaxis, linewidth=4, color='k')
ax.quiver(*origin, *zaxis, linewidth=4, color='k')

# Label the end of the vector with "X"
endX = np.array(origin) + np.array(xaxis) + [0.2, 0, 0]
endY = np.array(origin) + np.array(yaxis) + [0, 0.2, 0]
endZ = np.array(origin) + np.array(zaxis) + [0, 0, 0.2]
ax.text(*endX, '  X', color='red', fontsize=20, ha='center', va='center')
ax.text(*endY,'  Y', color='red', fontsize=20, ha='center', va='center')
ax.text(*endZ, '  Z', color='red', fontsize=20, ha='center', va='center')

# Vectors
ax.quiver(*origin, *v0, color='gray', linestyle='dashed', linewidth=2.5, label='V0 = [0 0 1]')
ax.quiver(*origin, *v1, color='grey', linewidth=2.5, label='Rx(35.26) V0')
ax.quiver(*origin, *v2, color='m', linewidth=2.5, label = 'V2')
# 'label=')Ry(45) Rx(35.26) V0')
ax.quiver(*origin, *v3, color='m', linewidth=2.5, label = 'V3')
# label='Rz(90) Ry(45) Rx(35.26) V0')
ax.quiver(*origin, *v4, color='m', linewidth=2.5, label = 'V4')
# label='Rz(180) Ry(45) Rx(35.26) V0')
ax.quiver(*origin, *v5, color='m', linewidth=2.5, label = 'V5')
# label='Rz(270) Ry(45) Rx(35.26) V0')
ax.quiver(*origin, *v6, color='m', linewidth=2.5, label='Flip V2')
ax.quiver(*origin, *v7, color='m', linewidth=2.5, label='Flip V3')
ax.quiver(*origin, *v8, color='m', linewidth=2.5, label='Flip V4')
ax.quiver(*origin, *v9, color='m', linewidth=2.5, label='Flip V5')

# Axes settings
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

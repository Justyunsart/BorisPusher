import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Constants
k = 8.99e9   # Coulomb's constant (N·m²/C²)
Q = 1e-9     # Total charge on the ring (C)
R = 1.0      # Radius of the ring (m)

# Grid settings
grid_size = 101
middle = grid_size // 2
x = np.linspace(-2, 2, grid_size)
y = np.linspace(-2, 2, grid_size)
z = np.linspace(-2, 2, grid_size)
X, Y, Z = np.meshgrid(x, y, z)

# Initialize field components
Ex = np.zeros(X.shape)
Ey = np.zeros(Y.shape)
Ez = np.zeros(Z.shape)

# Discretize the ring
num_points = 200
theta = np.linspace(0, 2 * np.pi, num_points)
ring_x = R * np.cos(theta)
ring_y = R * np.sin(theta)
ring_z = np.zeros_like(theta)
dq = Q / num_points

# Compute E-field from each ring element
for i in range(num_points):
    rx = X - ring_x[i]
    ry = Y - ring_y[i]
    rz = Z - ring_z[i]
    r = np.sqrt(rx**2 + ry**2 + rz**2)
    r3 = np.where(r != 0, r**3, np.inf)  # avoid division by zero
    Ex += k * dq * rx / r3
    Ey += k * dq * ry / r3
    Ez += k * dq * rz / r3

# Normalize vectors for quiver
magnitude = np.sqrt(Ex**2 + Ey**2 + Ez**2)
print(magnitude.shape)
# Plotting the electric field vectors
fig = plt.figure(figsize=(10, 8))
#ax = fig.add_subplot(121, projection='3d')
ax1= fig.add_subplot(111)
ax1.plot(x,np.log(magnitude[:,middle,middle]))
'''
skip = (slice(None, None, 2), slice(None, None, 2), slice(None, None, 2))  # Skip points to reduce clutter

ax.quiver(
    X[skip], Y[skip], Z[skip],
    Ex[skip] / magnitude[skip],
    Ey[skip] / magnitude[skip],
    Ez[skip] / magnitude[skip],
    length=0.2, normalize=True, color='blue', linewidth=0.5
)

# Plot the ring
ax.plot(R * np.cos(theta), R * np.sin(theta), np.zeros_like(theta), 'r-', linewidth=2)

ax.set_title('3D Electric Field of a Ring of Charge')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_box_aspect([1, 1, 1])
'''
plt.tight_layout()
plt.show()
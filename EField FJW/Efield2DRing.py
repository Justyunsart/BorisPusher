import numpy as np
import matplotlib.pyplot as plt

# Constants
k = 8.987551787e9  # Coulomb constant in N·m²/C²
R = 1.0            # Radius of the ring (m)
Q = 1e-9           # Total charge on the ring (C)
N_ring = 200       # Number of charge elements

# Discretize the ring (in xy-plane, z=0)
theta = np.linspace(0, 2 * np.pi, N_ring, endpoint=False)
ring_x = R * np.cos(theta)
ring_y = R * np.sin(theta)
ring_z = np.zeros_like(theta)
dq = Q / N_ring

# Observation grid in x–z plane (y=0)
grid_pts = 50
x_vals = np.linspace(-2, 2, grid_pts)
z_vals = np.linspace(-2, 2, grid_pts)
X, Z = np.meshgrid(x_vals, z_vals)
Y = np.zeros_like(X)  # y=0 plane

# Initialize E-field components
Ex = np.zeros_like(X)
Ez = np.zeros_like(Z)

# Compute E field at each grid point
for i in range(N_ring):
    rx = X - ring_x[i]
    ry = Y - ring_y[i]  # Always 0
    rz = Z - ring_z[i]
    r_squared = rx**2 + ry**2 + rz**2
    r_norm = np.sqrt(r_squared)
    r_cubed = r_squared * r_norm + 1e-20

    Ex += k * dq * rx / r_cubed
    Ez += k * dq * rz / r_cubed

# Plot streamlines
fig, ax = plt.subplots(figsize=(8, 6))
color = np.log(np.sqrt(Ex**2 + Ez**2))
strm = ax.streamplot(X, Z, Ex, Ez, color=color, linewidth=1, cmap='viridis', density=1.5)
ax.set_title('Electric Field Streamlines in x–z Plane')
ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')

# Draw the ring projection (at z=0)
circle = plt.Circle((0, 0), R, color='red', fill=False, linewidth=2)
ax.add_artist(circle)

plt.axis('equal')
plt.tight_layout()
plt.show()

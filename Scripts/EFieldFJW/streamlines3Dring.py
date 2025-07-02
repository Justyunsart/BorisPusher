import numpy as np
import matplotlib.pyplot as plt

# Physical constants and parameters
epsilon_0 = 8.854e-12  # Vacuum permittivity (F/m)
Q = 1e-9               # Total charge on the ring (Coulombs)
a = 1.0                # Radius of the ring (meters)
lambda_ = Q / (2 * np.pi * a)  # Linear charge density

# Define the electric field components
def integrand_Er(theta, r, z):
    D = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return (r - a * np.cos(theta)) / D**3

def integrand_Ez(theta, r, z):
    D = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return 1 / D**3

def compute_field(r, z):
    theta = np.linspace(0, 2 * np.pi, 500)
    dtheta = theta[1] - theta[0]
    int_Er = np.sum(integrand_Er(theta, r, z)) * dtheta
    int_Ez = np.sum(integrand_Ez(theta, r, z)) * dtheta
    E_r = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * int_Er
    E_z = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * z * int_Ez
    return E_r, E_z

# Grid setup in r-z plane
r_vals = np.linspace(0.1, 2.0, 40)
z_vals = np.linspace(-2.0, 2.0, 40)
R, Z = np.meshgrid(r_vals, z_vals)

# Compute field components
E_r = np.zeros_like(R)
E_z = np.zeros_like(Z)

for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        E_r[i, j], E_z[i, j] = compute_field(R[i, j], Z[i, j])

# Streamplot requires 2D Cartesian grid
X = R
Y = Z
U = E_r
V = E_z

# Plot streamlines
fig, ax = plt.subplots(figsize=(10, 6))
strm = ax.streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='viridis', density=1.2)

# # Plot the ring in r-z plane (circular ring at z=0)
# theta_ring = np.linspace(0, 2 * np.pi, 200)
# ring_x = a * np.cos(theta_ring)
# ring_y = a * np.sin(theta_ring)
# ax.plot(ring_x, ring_y, 'r', linewidth=2, label='Ring of Charge')

# Define the x values for the line
x_values = [-1, 1]
# Define the y values (constant at 0 for a horizontal line)
y_values = [0, 0]

# Plot the line
ax.plot(x_values, y_values, color='red', linewidth=4, label="Ring of Charge")

# Labels and formatting
ax.set_title('Electric Field Streamlines of a Ring of Charge (2D slice)')
ax.set_xlabel('r (m)')
ax.set_ylabel('z (m)')
ax.legend()
fig.colorbar(strm.lines, ax=ax, label='Electric Field Magnitude (a.u.)')
ax.axis('equal')
ax.grid(True)
plt.tight_layout()
plt.show()

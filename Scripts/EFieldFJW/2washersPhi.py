import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from scipy.special import ellipk
from scipy.integrate import simpson

# Parameters
Q = 1e-11  # charge per disk [C]
a = 0.25   # inner radius [m]
b = 1.0    # outer radius [m]
sigma = Q / (np.pi * (b**2 - a**2))  # surface charge density [C/m^2]
disk_separation = 2.0
z_centers = [-disk_separation/2, disk_separation/2]

# Radial integration grid
R = np.linspace(a, b, 500)

def k_squared(R, rho, z):
    return 4 * R * rho / ((R + rho)**2 + z**2)

def phi_single_disk(rho, z, z0):
    """Scalar potential from a single annular disk centered at z0."""
    z_shift = z - z0
    k2 = k_squared(R[:, None], rho[None, :], z_shift)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    denom = np.sqrt((R[:, None] + rho[None, :])**2 + z_shift**2)
    integrand = R[:, None] * K / denom
    result = simpson(integrand, R, axis=0)
    return sigma / (2 * epsilon_0) * result

def total_phi_grid(rho, z):
    """Compute total scalar potential on a 2D grid (rho, z)."""
    phi = np.zeros_like(rho)
    phi += phi_single_disk(rho, z, z_centers[0])      # lower disk, +z normal
    phi += phi_single_disk(rho, z, z_centers[1])      # upper disk, -z normal
    return phi

def compute_field_grid(rho_vals, z_vals):
    """Compute Erho and Ez on a 2D mesh grid."""
    RHO, Z = np.meshgrid(rho_vals, z_vals)
    phi_grid = np.zeros_like(RHO)
    for i, z in enumerate(z_vals):
        phi_grid[i, :] = total_phi_grid(rho_vals, z)

    drho = rho_vals[1] - rho_vals[0]
    dz = z_vals[1] - z_vals[0]
    Erho = -np.gradient(phi_grid, drho, axis=1, edge_order=2)
    Ez = -np.gradient(phi_grid, dz, axis=0, edge_order=2)
    return RHO, Z, Erho, Ez

# Grid for streamline plot
rho_vals = np.linspace(0.01, 1.5, 200)
z_vals = np.linspace(-1.2, 1.2, 200)
RHO, Z, Erho, Ez = compute_field_grid(rho_vals, z_vals)

# Convert cylindrical (rho,z) components to cartesian (x,z) for streamplot
X = RHO
Y = Z
U = Erho  # horizontal component
V = Ez    # vertical component

# Plot streamlines
plt.figure(figsize=(8, 10))
strm = plt.streamplot(X, Y, U, V, color=np.log(np.sqrt(U**2 + V**2)), linewidth=1.2, cmap='plasma', density=1.5)

# Draw a solid line on the plots
x_values = [a, b]
y_values = [z_centers, z_centers]
plt.plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
plt.plot(x_values, np.multiply(y_values, -1), color='green', linewidth=6, label="Charged Conductor")


plt.xlabel(r'Radial distance, $\rho$ (m)')
plt.ylabel(r'Axial distance, $z$ (m)')
plt.title("Electric Field Streamlines Between Two Facing Annular Disks")
plt.colorbar(strm.lines, label=r'$\log|\vec{E}|$ (V/m)')
plt.grid(True)
plt.axis('tight')
plt.xlim(0, 1.5)
plt.ylim(-1.2, 1.2)
plt.show()

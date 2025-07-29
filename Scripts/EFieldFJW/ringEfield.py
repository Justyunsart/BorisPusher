"""
This script generates and plots the 2D electric field produced by a charged ring.
Plots include a streamline, contour, and line-outs for the radial and axial magnitudes.
It demonstrates how to include a variable in a matplotlib legend using LaTeX-style
math symbols. The script also shows best practices for documenting and labeling
plots for clear presentation.

Author: F. Wessel
Date: July 8, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from matplotlib.colors import LogNorm

# Physical constants and parameters
Q = 1e-11               # Total charge on the ring (Coulombs)
a = 1.0                # Radius of the ring (meters)
lambda_ = Q / (2 * np.pi * a)  # Linear charge density
prefactor = lambda_*a/(4*np.pi*epsilon_0) # Vacuum permittivity, epsilon_0 = 8.854e-12 (F/m)

# Grid setup in r-z plane, streamplot requires 2D Cartesian grid
rho_vals = np.linspace(0.01, 1.5, 200)
z_vals = np.linspace(-0.25, 1.5, 200)
RHO, Z = np.meshgrid(rho_vals, z_vals)
theta = np.linspace(0, 2 * np.pi, 100)
dtheta = theta[1] - theta[0]
E_r = np.zeros_like(RHO)
E_z = np.zeros_like(Z)

# Define the electric field components
def integrand_Er(theta, r, z):
    D = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return (r - a * np.cos(theta)) / D**3

def integrand_Ez(theta, r, z):
    D = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return 1 / D**3

def compute_field(r, z):
    int_Er = np.sum(integrand_Er(theta, r, z)) * dtheta
    int_Ez = np.sum(integrand_Ez(theta, r, z)) * dtheta
    E_r = prefactor * int_Er
    # E_r = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * int_Er
    E_z = prefactor * z * int_Ez
    # E_z = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * z * int_Ez
    return E_r, E_z

# Compute field components and magnitude
for i in range(RHO.shape[0]):
    for j in range(RHO.shape[1]):
        E_r[i, j], E_z[i, j] = compute_field(RHO[i, j], Z[i, j])
E_m = np.sqrt(E_r ** 2 + E_z ** 2)

# Plot streamlines and contours
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(fr'Uniformly Charged Ring, radius a = {a} m, Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20)
c1 = axs[0,0].streamplot(RHO, Z, E_r, E_z, color=np.sqrt(E_r**2 + E_z**2), cmap='plasma', density=1.2)
fig.colorbar(c1.lines, ax=axs[0,0], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Create a pcolormesh with logarithmic normalization
c2 = axs[0, 1].pcolormesh(RHO, Z, E_m, norm=LogNorm(), cmap='plasma')
# Add a colorbar
cbar = fig.colorbar(c2, ax=axs[0, 1])
cbar.set_label('Log $|\\vec{E}|$ Field Magnitude (V/m)')

# Draw a dashed line and circle on the plots as the ring
x_values = [0, 1]
y_values = [0, 0]
x_values2 = [0.95, 1]
y_values2 = [0, 0]
axs[0,0].plot(x_values, y_values, color='red', linewidth=6, linestyle='dotted', label="Charged Ring")
axs[0,0].plot(x_values2, y_values2, color='green', linewidth=4, linestyle='solid')
axs[0,0].set_title('$\\vec{E}$ Field Streamlines')
axs[0,0].grid(True)
axs[0,0].legend()
axs[0,0].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0,0].set_ylabel(r'Axial Distance, $z$ (m)')
axs[0,1].plot(x_values, y_values, color='red', linewidth=6, linestyle='dotted', label="Charged Ring")
axs[0,1].plot(x_values2, y_values2, color='green', linewidth=6, linestyle='solid')
axs[0,1].set_title('$|\\vec{E}|$ Field Magnitude')
axs[0,1].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0,1].set_ylabel(r'Axial Distance, $z$ (m)')
axs[0,1].legend()

rho1 = 100
rho2 = 180
z_lo_min = 0.01 # line out distances
z_lo_vals = [z_lo_min,  5 * z_lo_min, 10 * z_lo_min, 50 * z_lo_min] # line out distances
for z_lineout in z_lo_vals:
    lineout_val = np.argmin(np.abs(z_vals - z_lineout))
    closest_value = z_vals[lineout_val]
    index = lineout_val
    axs[1, 0].plot(rho_vals, E_z[lineout_val, :], label=fr'{z_lineout} m')
    axs[1, 0].legend()
    axs[1, 1].plot(rho_vals, E_r[lineout_val, :], label=fr'{z_lineout} m')
    axs[1, 1].legend()
axs[1, 0].set_title('Radial Line-Outs for $\\vec{E}_z$ Field  at z = ')
axs[1, 0].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[1, 0].grid(True)
axs[1, 0].set_ylabel('Electric Field  (V/m)')
axs[1, 1].set_title('Radial Line-Outs for $\\vec{E}_{\\rho}$ Field  at z = ')
axs[1, 1].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[1, 1].set_ylabel('Electric Field  (V/m)')
axs[1, 1].grid(True)
plt.tight_layout()
plt.show()
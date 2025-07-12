"""
This script generates and plots the 2D electric field produced by a charged disk.
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
from numba import njit, prange
from matplotlib.colors import LogNorm

# Constants
Q = 1e-11 # Couloumb
a = 0.25 # Disk inner radius (m)
b = 1.0 # Disk outer radius (m)
Sigma = Q / (np.pi * (b ** 2 - a ** 2)) # charge density C/m^2
prefactor = Sigma / (4 * np.pi * epsilon_0)

# Integration resolution
Nr = 400
Ntheta = 400
r_vals = np.linspace(a, b, Nr)
theta_vals = np.linspace(0, 2*np.pi, Ntheta)
dr = r_vals[1] - r_vals[0]
dtheta = theta_vals[1] - theta_vals[0]

# Field grid
rho_vals = np.linspace(0.01, 1.5, 200)
z_vals = np.linspace(-0.25, 1, 200)
RHO, Z = np.meshgrid(rho_vals, z_vals)
E_rho = np.zeros_like(RHO)
E_z = np.zeros_like(Z)

@njit(parallel=True)
def compute_fields(E_rho, E_z, rho_vals, z_vals, r_vals, theta_vals, dr, dtheta):
    for i in prange(len(rho_vals)):
        for j in prange(len(z_vals)):
            rho = rho_vals[i]
            z = z_vals[j]
            Erho_sum = 0.0
            Ez_sum = 0.0

            for m in range(len(r_vals)):
                r = r_vals[m]
                for n in range(len(theta_vals)):
                    theta = theta_vals[n]
                    dx = rho - r * np.cos(theta)
                    dy = -r * np.sin(theta)
                    dz = z
                    Denom = (dx * dx + dy * dy + dz * dz) ** 1.5 + 1e-20  # prevent zero division
                    dA = r * dr * dtheta
                    Erho_sum += dx * dA / Denom
                    Ez_sum += dz * dA / Denom
            E_rho[j, i] = prefactor * Erho_sum
            E_z[j, i] = prefactor * Ez_sum

# Calculate the field and total field magnitude
compute_fields(E_rho, E_z, rho_vals, z_vals, r_vals, theta_vals, dr, dtheta)
E_mag = np.sqrt(E_rho**2 + E_z**2)

# Plot
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(fr'Uniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20)

c1 = axs[0,0].streamplot(RHO, Z, E_rho, E_z, color=np.sqrt(E_rho**2 + E_z**2), cmap='plasma', density=1.2)
fig.colorbar(c1.lines, ax=axs[0,0], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Create a pcolormesh with logarithmic normalization
c2 = axs[0,1].pcolormesh(RHO, Z, E_mag, norm=LogNorm(), cmap='plasma')
# fig.colorbar(np.log(E_mag), ax=axs[0,1], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Add a colorbar
cbar = fig.colorbar(c2, ax=axs[0,1])
cbar.set_label('Log $|\\vec{E}|$ Field Magnitude (V/m)')

# Draw a solid line on the plots
x_values = [a, b]
y_values = [0, 0]
axs[0,0].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0,1].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0,0].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0,0].set_ylabel(r'Axial Distance, $z$ (m)')
axs[0,1].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0,1].set_ylabel(r'Axial Distance, $z$ (m)')
axs[0,0].grid(True)
axs[0,0].legend()
axs[0,1].legend()
axs[0,1].grid(True)
axs[0,0].set_title('$\\vec{E}$ Field Streamlines')
axs[0,1].set_title('$\\vec{E}$ Field Magnitude')

rho1 = 100
rho2 = 180
z_lo_min = 0.01
z_lo_vals = [z_lo_min,  5 * z_lo_min, 10 * z_lo_min, 50 * z_lo_min]
for z_lineout in z_lo_vals:
    lineout_val = np.argmin(np.abs(z_vals - z_lineout))
    closest_value = z_vals[lineout_val]
    index = lineout_val
    axs[1,0].plot(rho_vals, E_rho[lineout_val, :], label= fr'{z_lineout} mm')
    axs[1,1].plot(rho_vals, E_z[lineout_val, :], label = fr'{z_lineout} mm')
    axs[1,0].legend()
    axs[1,1].legend()
axs[1,0].set_title('Radial Line-Outs for $\\vec{E}_{\\rho}$ Field Magnitude at z = ')
axs[1,0].set_xlabel(r'radial distance, $\rho$ (m)')
axs[1,0].grid(True)
axs[1,0].set_ylabel('Electric Field Magnitude (V/m)')
axs[1,1].set_title('Radial Line-Outs for $|\\vec{E}_z|$ Field Magnitude at z = ')
axs[1,1].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[1,1].set_ylabel('Electric Field Magnitude (V/m)')
axs[1,1].grid(True)
plt.tight_layout()
plt.show()

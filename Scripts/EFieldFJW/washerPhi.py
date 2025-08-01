"""
This script generates and plots the 2D electric field produced by a charged disk.
Plots include a streamline, contour, and line-outs for the radial and axial magnitudes.
It demonstrates how to include a variable in a matplotlib legend using LaTeX-style
math symbols. The script also shows best practices for documenting and labeling
plots for clear presentation.

Author: F. Wessel
Date: July 12, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from numba import njit, prange
from matplotlib.colors import LogNorm
import textwrap

# Constants
Q = 1e-11 # Couloumb
a = 0.25 # Disk inner radius (m)
b = 1.0 # Disk outer radius (m)
sigma_denominator = np.pi*(b**2 - a**2)
sigma = Q / sigma_denominator
prefactor = sigma / (4 * np.pi * epsilon_0)

# integration grid
Nr = 400
Ntheta = 400
r_vals = np.linspace(a, b, Nr)
theta_vals = np.linspace(0, 2*np.pi, Ntheta)
dr = r_vals[1] - r_vals[0]
dtheta = theta_vals[1] - theta_vals[0]

# Field grid
rho_vals = np.linspace(0.01, 1.5, 200)  # meters
z_vals = np.linspace(-0.25, 1, 200)    # meters
RHO, Z = np.meshgrid(rho_vals, z_vals)
E_rho = np.zeros_like(RHO)
E_z = np.zeros_like(Z)
Phi = np.zeros_like(RHO) #

@njit(parallel=True)
def compute_potential(Phi, rho_vals, z_vals, r_vals, theta_vals, dr, dtheta):
    for i in prange(len(rho_vals)):
        for j in prange(len(z_vals)):
            rho = rho_vals[i]
            z = z_vals[j]
            Phi_sum = 0.0

            for m in range(len(r_vals)):
                r = r_vals[m]
                for n in range(len(theta_vals)):
                    theta = theta_vals[n]
                    dx = rho - r * np.cos(theta)
                    dy = -r * np.sin(theta)
                    dz = z
                    Denom = (dx * dx + dy * dy + dz * dz) ** 0.5 + 1e-20  # prevent zero division
                    dA = r * dr * dtheta
                    Phi_sum += dA / Denom
            Phi[j, i] = prefactor * Phi_sum

# Compute electric field from gradient
compute_potential(Phi, rho_vals, z_vals, r_vals, theta_vals, dr, dtheta)

# Compute grid spacing
d_rho = rho_vals[1] - rho_vals[0]
d_z = z_vals[1] - z_vals[0]
dPhi_dz,  dPhi_drho = np.gradient(Phi,d_rho, d_z, edge_order=1) # note the rho, z order for Phi
E_rho = -dPhi_drho
E_z = -dPhi_dz
E_mag = np.sqrt(E_rho**2 + E_z**2)


# Plot potential
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
title = fr"Electric Field Calculated from a Scalar Potential for a Uniformly-Charged Washer, radii a, b = {a}, {b} m, Centered at (X, Y, 0), $Q = 10^{{-11}}$ C"
wrapped = "\n".join(textwrap.wrap(title, width = 60))
    # fig.suptitle(fr'Electric Field Calculated from a Scalar Potential for a \nUniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20))
fig.suptitle(wrapped, fontsize=20)
fig.tight_layout(rect=[0, 0, 1, 0.95])  # reserve space for suptitle

c1 = axs[0, 0].streamplot(RHO, Z, E_rho, E_z, color=np.sqrt(E_rho**2 + E_z**2), cmap='plasma', density=1.2)
fig.colorbar(c1.lines, ax=axs[0, 0], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Create a pcolormesh with logarithmic normalization
c2 = axs[0, 1].pcolormesh(RHO, Z, E_mag, norm=LogNorm(), cmap='plasma')
# fig.colorbar(np.log(E_mag), ax=axs[0,1], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Add a colorbar
cbar = fig.colorbar(c2, ax=axs[0, 1])
cbar.set_label('Log $|\\vec{E}|$ Field Magnitude (V/m)')
# Draw a solid line on the plots
x_values = [a, b]
y_values = [0, 0]
axs[0, 0].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0, 1].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0, 0].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0, 0].set_ylabel(r'Axial Distance, $z$ (m)')
axs[0, 1].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0, 1].set_ylabel(r'Axial Distance, $z$ (m)')
axs[0, 0].grid(True)
axs[0, 0].legend()
axs[0, 1].legend()
axs[0, 1].grid(True)
axs[0, 0].set_title('$\\vec{E}$ Field Streamlines')
axs[0, 1].set_title('$\\vec{E}$ Field Magnitude')
#
rho1 = 100
rho2 = 180
z_lo_min = 0.01 # z axis lineouts
z_lo_vals = [z_lo_min, 5 * z_lo_min, 10 * z_lo_min, 50 * z_lo_min]  # z axis lineouts
for z_lineout in z_lo_vals:
    lineout_val = np.argmin(np.abs(z_vals - z_lineout))
    closest_value = z_vals[lineout_val]
    index = lineout_val
    axs[1, 0].plot(rho_vals, E_z[lineout_val, :], label=fr'{z_lineout} m')
    axs[1, 1].plot(rho_vals, E_rho[lineout_val, :], label=fr'{z_lineout} m')
    axs[1, 0].legend()
    axs[1, 1].legend()
axs[1, 0].set_title('Radial Line-Outs for $\\vec{E}_z$ Field  at z = ')
axs[1, 0].set_xlabel(r'radial distance, $\rho$ (m)')
axs[1, 0].grid(True)
axs[1, 0].set_ylabel('Electric Field (V/m)')
axs[1, 1].set_title('Radial Line-Outs for $\\vec{E}_{\\rho}$ Field at z = ')
axs[1, 1].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[1, 1].set_ylabel('Electric Field  (V/m)')
axs[1, 1].grid(True)

plt.tight_layout()
plt.show()
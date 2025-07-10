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

# Constants
Q = 1e-11 # Couloumb
a = 1.0 # Disk radius (m)
Sigma = Q / (np.pi * a ** 2) # charge density C/m^2
prefactor = Sigma / (4 * np.pi * epsilon_0)

# Integration resolution
Nr = 100
Ntheta = 100
r_vals = np.linspace(0, a, Nr)
theta_vals = np.linspace(0, 2*np.pi, Ntheta)
dr = r_vals[1] - r_vals[0]
dtheta = theta_vals[1] - theta_vals[0]

# Field grid
rho_vals = np.linspace(0.01, 1.5, 200)
z_vals = np.linspace(0.01, 1, 200)

RHO, Z = np.meshgrid(rho_vals, z_vals)
#print(RHO.shape)
#_g = np.column_stack((RHO, Z))
#print(_g.shape)

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
                    Erho_sum += dx / Denom * dA
                    Ez_sum += dz / Denom * dA

            E_rho[j, i] = prefactor * Erho_sum
            E_z[j, i] = prefactor * Ez_sum

# Calculate the field and total field magnitude
compute_fields(E_rho, E_z, rho_vals, z_vals, r_vals, theta_vals, dr, dtheta)
E_mag = np.sqrt(E_rho**2 + E_z**2)

# @njit()
def compute_single_point_fields(rho, z, r_vals, theta_vals, dr, dtheta):
    Erho_sum = 0.0
    Ez_sum = 0.0
    for m in range(len(r_vals)):
        r = r_vals[m]
        for n in range(len(theta_vals)):
            theta = theta_vals[n]
            dx = rho - r * np.cos(theta)
            dy = -r * np.sin(theta)
            dz = z
            denom = (dx*dx + dy*dy + dz*dz)**1.5 + 1e-20  # avoid div0
            dA = r * dr * dtheta
            Erho_sum += dx / denom * dA
            Ez_sum += dz / denom * dA
    # coef = (sigma / (4 * np.pi * eps0))
    return prefactor * Erho_sum, prefactor * Ez_sum

# Plot
# levels = np.linspace(0, 1.0, 10, endpoint=True)
fig, axs = plt.subplots(3, 2, figsize=(14, 10))
fig.suptitle('Uniformly Charged Disk: X-Y Plane at Z = 0 with $Q_{total} = 10^{-11}$ C') # or plt.suptitle('Main title')
c1 = axs[0,0].streamplot(RHO, Z, E_rho, E_z, color=np.sqrt(E_rho**2 + E_z**2), cmap='plasma', density=1.2)
c2 = axs[0,1].contourf(RHO, Z, E_mag, levels=20, cmap='plasma')
fig.colorbar(c1.lines, ax=axs[0,0], label='|E| (V/m)')
fig.colorbar(c2, ax=axs[0,1], label='|E| (V/m)')
# Draw a solid line on the plots
x_values = [0, 1]
y_values = [0, 0]
axs[0,0].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0,1].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0,0].set_xlabel(r'$\rho$ (m)')
axs[0,0].set_ylabel(r'$z$ (m)')
axs[0,1].set_xlabel(r'$\rho$ (m)')
axs[0,1].set_ylabel(r'$z$ (m)')
axs[0,0].grid(True)
axs[0,0].legend()
axs[0,1].legend()
axs[0,1].grid(True)
axs[0,0].set_title('$\\vec{E}$ Field Streamlines')
axs[0,1].set_title('$\\vec{E}$ Field Magnitude $|\\vec{E}|$')
#
# Calculate line-out fields Erho and Ez along radius, for variable z positions
z_lo_vals = np.array([np.min(z_vals) + 0.005, 5 * np.min(z_vals), 10 * np.min(z_vals), 50 * np.min(z_vals)])
rho_line = np.linspace(0.001, 1.5, 400)
E_rho_line = np.zeros_like(rho_line)
E_z_line = np.zeros_like(rho_line)
for z_lineout in z_lo_vals:
    lineout_val = np.argmin(np.abs(z_vals - z_lineout))
    closest_value = z_vals[lineout_val]
    index = lineout_val
    for i in range(len(rho_line)):
        E_rho_line[i], E_z_line[i] = (compute_single_point_fields(rho_line[i], z_lineout, r_vals, theta_vals, dr, dtheta))
    c3 = axs[1,0].plot(rho_line, np.abs(E_rho_line), label= fr'z = {z_lineout} mm')
    c4 = axs[1,1].plot(rho_line, np.abs(E_z_line), label = fr'z = {z_lineout} mm')
    axs[1,0].legend()
    axs[1,1].legend()
#
axs[1,0].set_xlabel(r'$\rho$ (m)')
axs[1,0].set_ylabel('Electric field magnitude (V/m)')
axs[1,0].set_title(fr'Line-Outs for the Radial Field Magnitude, $|E_\rho|$')
axs[1,1].set_xlabel(r'$\rho$ (m)')
axs[1,1].set_ylabel('Electric field magnitude (V/m)')
axs[1,1].set_title(fr'Line-Outs for the Axial Field Magnitude, $|E_z|$')
axs[1,0].grid(True)
axs[1,1].grid(True)

rho1 = 100
rho2 = 180
z_lo_vals = np.array([np.min(z_vals) + 0.005, 5 * np.min(z_vals), 10 * np.min(z_vals), 50 * np.min(z_vals)])
for z_lineout in z_lo_vals:
    lineout_val = np.argmin(np.abs(z_vals - z_lineout))
    # print(lineout_val)
    closest_value = z_vals[lineout_val]
    # print(closest_value)
    index = lineout_val
    # print(index)
    axs[2,0].plot(rho_vals, E_rho[lineout_val, :], label= fr'{z_lineout} mm')
    axs[2,1].plot(rho_vals, E_z[lineout_val, :], label = fr'{z_lineout} mm')
    axs[2,0].legend()
    axs[2,1].legend()
axs[2,0].set_title(fr'Line-Outs for the Radial Field Magnitude, $|E_\rho|$, z = ')
axs[2,1].set_title(fr'Line-Outs for the Radial Field Magnitude, $|E_z|$, z = ')
axs[2,0].set_xlabel(r'$\rho$ (m)')
axs[2,1].set_ylabel('Electric field magnitude (V/m)')
axs[2,1].set_xlabel(r'$\rho$ (m)')
axs[2,1].set_ylabel('Electric field magnitude (V/m)')
axs[2,0].grid(True)
axs[2,1].grid(True)
# plt.tight_layout()
plt.show()

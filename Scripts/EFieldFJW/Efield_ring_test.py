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
from numba import njit, prange
# import matplotlib as m
# Computes the electric field due to a uniformly charged ring.
# Plots data for the radial and axial field components

# Physical constants and parameters
# epsilon_0 = 8.854e-12  # Vacuum permittivity (F/m)
Q = 1e-11               # Total charge on the ring (Coulombs)
a = 1.0                # Radius of the ring (meters)
lambda_ = Q / (2 * np.pi * a)  # Linear charge density
prefactor = lambda_*a/(4*np.pi*epsilon_0)

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
    E_r = prefactor * int_Er
    # E_r = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * int_Er
    E_z = prefactor * z * int_Ez
    # E_z = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * z * int_Ez
    return E_r, E_z

# Grid setup in r-z plane, streamplot requires 2D Cartesian grid
r_vals = np.linspace(0.1, 2.0, 300)
z_vals = np.linspace(0.01, 2.0, 300)
R, Z = np.meshgrid(r_vals, z_vals)

# Compute field components and magnitude
E_r = np.zeros_like(R)
E_z = np.zeros_like(Z)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        E_r[i, j], E_z[i, j] = compute_field(R[i, j], Z[i, j])
E_m = np.sqrt(E_r ** 2 + E_z ** 2)

# Plot streamlines and contours
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Uniformly Charged Ring: X-Y Plane at Z = 0 with $Q_{total} = 10^{-11}$ C') # or plt.suptitle('Main title')
c1 = axs[0,0].streamplot(R, Z, E_r, E_z, color=np.sqrt(E_r**2 + E_z**2), cmap='plasma', density=1.2)
fig.colorbar(c1.lines, ax=axs[0,0], label='|E| (V/m)')
c2 = axs[0,1].contourf(R, Z, E_m, levels=20, cmap='plasma')
fig.colorbar(c2, ax=axs[0,1], label='|E| (V/m)')
# axs[0,0].axis('equal')
# Draw a solid line on the plots
x_values = [0, 1]
y_values = [0, 0]
axs[0,0].plot(x_values, y_values, color='green', linewidth=6, linestyle='dotted', label="Charged Ring")
# axs[0,0].Circle(( 1.0 , 0.0 ), 0.2 )
axs[0,0].set_title('$\\vec{E}$ Field Streamlines')
axs[0,0].grid(True)
axs[0,0].legend()
axs[0,0].set_xlabel(r'$\rho$ (m)')
axs[0,0].set_ylabel(r'$z$ (m)')

axs[0,1].plot(x_values, y_values, color='green', linewidth=6,  linestyle='dotted', label="Charged Ring")
axs[0,1].set_title('$|\\vec{E}|$ Field Magnitude')
axs[0,1].set_xlabel(r'$\rho$ (m)')
axs[0,1].set_ylabel(r'$z$ (m)')
axs[0,1].legend()

rho1 = 100
rho2 = 180
axs[1,0].plot(r_vals, E_r[ : , 100 ], label=r'$|E_r|$', color='blue')
axs[1,1].plot(r_vals, E_z[ : , 100 ], label=r'$|E_r|$', color='blue')

plt.show()


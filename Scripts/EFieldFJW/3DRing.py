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
z_vals = np.linspace(0.01, 2.0, 100)
R, Z = np.meshgrid(r_vals, z_vals)

# Compute field components and magnitude
E_r = np.zeros_like(R)
E_z = np.zeros_like(Z)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        E_r[i, j], E_z[i, j] = compute_field(R[i, j], Z[i, j])
E_m = np.sqrt(E_r ** 2 + E_z ** 2)

# cm = m.colors.LinearSegmentedColormap('viridis', 1024)

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

# c3 = axs[1,0].contourf(X, Y, U, levels=50, cmap='plasma')
# c4 = axs[2,0].contourf(X, Y, V, levels=50, cmap='plasma')

# Display a circular ring in r-z plane, centered at z = 0
# theta_ring = np.linspace(0, 2 * np.pi, 200)
# ring_x = a * np.cos(theta_ring)
# ring_y = a * np.sin(theta_ring)
# ax.plot(ring_x, ring_y, 'r', linewidth=2, label='Ring of Charge')

# Labels and formatting
# axs[1,0].set_title('$|\\vec{E}|$ Radial Component, $|\\vec{E_r}|$')
# axs[2,0].set_title('$|\\vec{E}|$ Axial Component, $|\\vec{E_z}|$')
# axs[2,0].set_xlabel('r (m)')
# axs[2,0].set_ylabel('z (m)')
# fig.colorbar(c3, ax=axs[1,0], label='Field Magnitude (a.u.)')
# fig.colorbar(c4, ax=axs[2,0], label='Field Magnitude (a.u.)')


z_fixed = 0.01  # 1 mm above the ring
E_rho_vals = []
E_z_vals = []
theta = np.linspace(0, 2 * np.pi, 500)
dtheta = theta[1] - theta[0]
cos_phi = np.cos(theta)

# Compute line outs for E_rho and E_z at fixed height
# @njit()
for rho in r_vals:
    D2 = np.sqrt(rho ** 2 + a ** 2 - 2 * rho * a * cos_phi + z_fixed ** 2)

    dE_rho = (rho - a * cos_phi) / D2 ** 3
    dE_z = z_fixed / D2 ** 3

    E_rho = np.sum(dE_rho) * dtheta
    E_z = np.sum(dE_z) * dtheta

    E_rho_vals.append(E_rho)
    E_z_vals.append(E_z)
# Scale both components by the Coulomb constant
# prefactor = lambda_ * R / (4 * np.pi * epsilon_0)
E_rho_vals = prefactor * np.array(E_rho_vals)
E_z_vals = prefactor * np.array(E_z_vals)

rho1 = 100
rho2 = 180
c5 = axs[1,0].plot(r_vals[rho1:rho2], E_rho_vals[rho1:rho2], label=r'$|E_r|$', color='blue')
c6 = axs[1,1].plot(r_vals[rho1:rho2], E_z_vals[rho1:rho2], label=r'$|E_z|$', color='green')
axs[1,0].set_title('Line-Out for the Radial E Field  at z =  10 mm')
axs[1,1].set_title('Line-Out for the Axial E Field  at z =  10 mm')
axs[1,0].set_xlabel(r'$\rho$ (m)')
axs[1,1].set_xlabel(r'$\rho$ (m)')
axs[1,0].set_ylabel('Electric field magnitude (V/m)')
axs[1,1].set_ylabel('Electric field magnitude (V/m)')
axs[1,0].grid(True)
axs[1,1].grid(True)

plt.show()

# axs[1,0].set_ylabel('z (m)')
# axs[2,1].set_xlabel('r (m)')
# axs[2,1].set_ylabel('Magnitude (V/m)')
# axs[2,0].legend()
# axs[2,1].legend()

# plt.tight_layout()

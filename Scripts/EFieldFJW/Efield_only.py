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

# Constants
Q = 1e-11 # Couloumb
a = 1.0 # Disk radius (m)
Lambda = Q / (2 * np.pi * a)  # Linear charge density
prefactor = Lambda / (4 * np.pi * epsilon_0)

# Integration resolution
Nr = 100
Ntheta = 100
r_vals = np.linspace(0, a, Nr)
theta_vals = np.linspace(0, 2*np.pi, Ntheta)
dr = r_vals[1] - r_vals[0]
dtheta = theta_vals[1] - theta_vals[0]

# Define the electric field components
def integrand_Er(theta, r, z):
    Denom = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return (r - a * np.cos(theta)) / Denom**3

def integrand_Ez(theta, r, z):
    Denom = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return 1 / Denom**3

def compute_field(r, z):
    theta = np.linspace(0, 2 * np.pi, 500)
    dtheta = theta[1] - theta[0]
    int_Er = np.sum(integrand_Er(theta, r, z)) * dtheta
    int_Ez = np.sum(integrand_Ez(theta, r, z)) * dtheta
    E_r = prefactor * a * int_Er
    # E_r = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * int_Er
    E_z = prefactor * z * int_Ez
    # E_z = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * z * int_Ez
    return E_r, E_z

# Grid setup in r-z plane
r_vals = np.linspace(0.1, 2.0, 300)
z_vals = np.linspace(0.01, 2.0, 100)
R, Z = np.meshgrid(r_vals, z_vals)

# Compute field components
E_r = np.zeros_like(R)
E_z = np.zeros_like(Z)

for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        E_r[i, j], E_z[i, j] = compute_field(R[i, j], Z[i, j])
# Compute field magnitude
E_m = np.sqrt(E_r ** 2 + E_z ** 2)

# cm = m.colors.LinearSegmentedColormap('viridis', 1024)
# Streamplot requires 2D Cartesian grid
X = R
Y = Z
U = E_r # radial
V = E_z # axial
W = E_m # magnitude


# Plot streamlines and contours
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Uniformly Charged Ring: X-Y Plane at Z = 0 with $Q_{total} = 10^{-11}$ C') # or plt.suptitle('Main title')

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
            denom = (dx * dx + dy * dy + dz * dz) ** 1.5 + 1e-20  # avoid div0
            dA = r * dr * dtheta
            Erho_sum += dx / denom * dA
            Ez_sum += dz / denom * dA
    # coef = (sigma / (4 * np.pi * eps0))
    return prefactor * Erho_sum, prefactor * Ez_sum

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


z_fixed = 0.01  # 1 mm above the ring
E_rho_vals = []
E_z_vals = []
theta = np.linspace(0, 2 * np.pi, 500)
dtheta = theta[1] - theta[0]
cos_phi = np.cos(theta)

# Compute E_rho and E_z for each radial point at fixed height

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
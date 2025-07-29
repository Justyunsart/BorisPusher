"""
This script generates and plots the 2D electric field produced by a charged annular disk.
Plots include a streamline, contour, and line-outs for the radial and axial magnitudes.
It includes a variable in the matplotlib legend using LaTeX-style
math symbols.
Author: F. Wessel
Date: July 27, 2025
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from scipy.special import ellipk
from scipy.integrate import simpson
import textwrap


# Parameters
Q = 10**-11
a = 0.25      # Inner radius [m]
b = 1.0      # Outer radius [m]
sigma_denominator = np.pi*(b**2 -a**2)
sigma = Q/sigma_denominator  # C/m^2

# Integration grid
R = np.linspace(a, b, 150)
dR = R[1] - R[0]


def k_squared(R, rho, z):
    return 4 * R * rho / ((R + rho) ** 2 + z ** 2)

def phi(rho, z):
    """Scalar potential at (rho, z) from annular disk."""
    k2 = k_squared(R[:, None], rho[None, :], z)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    denom = np.sqrt((R[:, None] + rho[None, :]) ** 2 + z ** 2)
    integrand = R[:, None] * K / denom
    result = simpson(integrand, R, axis=0)
    # result = np.trapezoid(integrand, R, axis=0)
    return sigma / (2 * epsilon_0) * result


def compute_field(rho, z):
    """Compute E_rho and E_z from -∇Phi numerically."""
    drho = rho[1] - rho[0]
    phi_grid = phi(rho, z)

    # Numerical derivatives
    E_rho = -np.gradient(phi_grid, drho, edge_order=2)
    dz = 1e-5
    phi_up = phi(rho, z + dz)
    phi_down = phi(rho, z - dz)
    E_z = -(phi_up - phi_down) / (2 * dz)

    return E_rho, E_z


# Evaluation points
rho_vals = np.linspace(0.01, 1.5, 300)
z_vals = [0.01, 0.05, 0.1, 0.5]

# Plot
fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharex=True)
title = fr"Electric Field Calculated from a Scalar Potential for a Uniformly-Charged Annular Disk, radii a, b = {a}, {b} m, Centered at (X, Y, 0), $Q = 10^{{-11}}$ C"
wrapped = "\n".join(textwrap.wrap(title, width = 60))
    # fig.suptitle(fr'Electric Field Calculated from a Scalar Potential for a \nUniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20))
fig.suptitle(wrapped, fontsize=20)
fig.tight_layout(rect=[0, 0, 1, 0.95])  # reserve space for suptitle

for z in z_vals:
    E_rho, E_z = compute_field(rho_vals, z)
    axs[0].plot(rho_vals, E_z, label=f' {z:.2f} m')
    axs[1].plot(rho_vals, E_rho, label=f' {z:.2f} m')
axs[0].set_xlabel(r'radial distance, $\rho$ (m)')
axs[0].set_ylabel(r'Electric Field, $E_z$ (V/m)')
axs[1].set_xlabel(r'radial distance, $\rho$ (m)')
axs[1].set_ylabel(r'Electric Field, $E_\rho$ (V/m)')
axs[0].set_title('Radial Line-Outs for $\\vec{E}_z$ Field  at z = ')
axs[1].set_title('Radial Line-Outs for $\\vec{E}_{\\rho}$ Field at z = ')
for ax in axs:
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.show()

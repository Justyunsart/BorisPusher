import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from scipy.special import ellipk
from scipy.integrate import simpson
import textwrap

# Disk Parameters
Q = 10**-11
a = 0.25      # Inner radius [m]
b = 1.0       # Outer radius [m]
sigma = Q / (np.pi * (b**2 - a**2))  # Uniform surface charge density [C/m^2]
disk_separation = 1.0                # Distance between disks [m]
z_centers = [-disk_separation / 2, +disk_separation / 2]  # z-locations of the disks

# Integration grid
R = np.linspace(a, b, 150)

def k_squared(R, rho, z):
    return 4 * R * rho / ((R + rho) ** 2 + z ** 2)

def phi_single_disk(rho, z, z0):
    """Scalar potential at (rho, z) from a single annular disk centered at z0."""
    z_shift = z - z0
    k2 = k_squared(R[:, None], rho[None, :], z_shift)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    denom = np.sqrt((R[:, None] + rho[None, :]) ** 2 + z_shift ** 2)
    integrand = R[:, None] * K / denom
    result = simpson(integrand, R, axis=0)
    return sigma / (2 * epsilon_0) * result

def total_phi(rho, z):
    """Total scalar potential from two annular disks facing each other."""
    phi1 = -phi_single_disk(rho, z, z_centers[0])          # lower disk (normal +z)
    phi2 = -phi_single_disk(rho, z, z_centers[1])         # upper disk flipped (normal -z)
    return phi1 + phi2


def compute_field(rho, z):
    """Compute E_rho and E_z from -∇Phi numerically."""
    drho = rho[1] - rho[0]
    phi_grid = total_phi(rho, z)

    # Numerical derivatives
    E_rho = -np.gradient(phi_grid, drho, edge_order=2)
    dz = 1e-5
    phi_up = total_phi(rho, z + dz)
    phi_down = total_phi(rho, z - dz)
    E_z = -(phi_up - phi_down) / (2 * dz)

    return E_rho, E_z

# Evaluation points
rho_vals = np.linspace(0.01, 1.5, 300)
z_vals = [-0.5, -0.1, -0.05, -0.01,0.0, 0.01, 0.05, 0.1, 0.5]

# Plot
fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharex=True)
title = fr"""Electric Field from Two Uniformly-Charged Annular Disks
(radii a, b = {a}, {b} m), Separated by 1 m, $Q = 10^{{-11}}$ C each"""
wrapped = "\n".join(textwrap.wrap(title, width=60))
fig.suptitle(wrapped, fontsize=18)
fig.tight_layout(rect=[0, 0, 1, 0.93])

for z in z_vals:
    E_rho, E_z = compute_field(rho_vals, z)
    axs[0].plot(rho_vals, E_z, label=f' z = {z:.2f} m')
    axs[1].plot(rho_vals, E_rho, label=f' z = {z:.2f} m')

axs[0].set_xlabel(r'radial distance, $\rho$ (m)')
axs[0].set_ylabel(r'Electric Field, $E_z$ (V/m)')
axs[1].set_xlabel(r'radial distance, $\rho$ (m)')
axs[1].set_ylabel(r'Electric Field, $E_\rho$ (V/m)')
axs[0].set_title('Axial Component $E_z$')
axs[1].set_title('Radial Component $E_\\rho$')

for ax in axs:
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.show()
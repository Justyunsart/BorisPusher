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



def k_squared(R, rho, z):
    return 4 * R * rho / ((R + rho) ** 2 + z ** 2)

def phi(rho, z, sigma, R):
    """Scalar potential at (rho, z) from annular disk."""
    k2 = k_squared(R[:, None], rho[None, :], z)
    k2 = np.clip(k2, 0, 1 - 1e-12)
    K = ellipk(k2)
    denom = np.sqrt((R[:, None] + rho[None, :]) ** 2 + z ** 2)
    integrand = R[:, None] * K / denom
    result = simpson(integrand, R, axis=0)
    # result = np.trapezoid(integrand, R, axis=0)
    return sigma / (2 * epsilon_0) * result


def compute_field(rho, z, Q, a, b, R_res=150):
    """Compute E_rho and E_z from -∇Phi numerically."""
    R = np.linspace(a, b, R_res)
    sigma_denominator = np.pi * (b ** 2 - a ** 2)
    sigma = Q / sigma_denominator  # C/m^2

    drho = rho[1] - rho[0]

    phi_grid = phi(rho, z, sigma, R)

    # Numerical derivatives
    E_rho = -np.gradient(phi_grid, drho, edge_order=2)
    dz = 1e-5
    phi_up = phi(rho, z + dz, sigma, R)
    phi_down = phi(rho, z - dz, sigma, R)
    E_z = -(phi_up - phi_down) / (2 * dz)

    return E_rho, E_z





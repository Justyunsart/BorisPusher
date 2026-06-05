import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# --- CONSTANTS & PARAMETERS ---
mu_0 = 4 * np.pi * 1e-7  # Permeability of free space [H/m]
a = 0.2  # Inner radius [m]
b = 0.8  # Outer radius [m]
z_prime = 1.0  # Axial offset [m]
I = 1e5  # Current per turn [A]
N = 10  # Number of turns
I_total = N * I  # Total current [A]

K_surf = I_total / (b - a)  # Surface current density [A/m]


def compute_A_theta(r, z):
    """
    Computes the azimuthal vector potential A_theta at a specific (r, z)
    by integrating the concentric filamentary loop contributions.
    """
    if r < 1e-9:
        return 0.0

    def integrand(r_prime):
        numerator = 4 * r * r_prime
        denominator = (r + r_prime) ** 2 + (z - z_prime) ** 2
        k2 = numerator / denominator

        if abs(k2 - 1.0) < 1e-9:
            return 0.0

        K = ellipk(k2)
        E = ellipe(k2)

        kernel = (1.0 / np.sqrt(denominator)) * (((2.0 - k2) * K - 2.0 * E) / k2)
        return r_prime * kernel

    integral_val, _ = quad(integrand, a, b, limit=100)
    return (mu_0 * K_surf / np.pi) * integral_val


# --- GENERATE PLOTTING GRID ---
# Using a slightly higher density grid to ensure smooth line trajectories
r_vals = np.linspace(0.001, 2.0, 120)
z_vals = np.linspace(0.0, 2.5, 120)
R, Z = np.meshgrid(r_vals, z_vals)

# Evaluate the vector potential array
A_theta_grid = np.zeros(R.shape)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        A_theta_grid[i, j] = compute_A_theta(R[i, j], Z[i, j])

# --- COMPUTE MAGNETIC FLUX FUNCTION (Psi = r * A_theta) ---
# Contours of Psi correspond exactly to magnetic field lines
Psi = R * A_theta_grid

# --- VISUALIZATION ---
fig, ax = plt.subplots(figsize=(10, 8))

# Background color mapping representing the field line intensity profile
contour_bg = ax.contourf(R, Z, Psi, levels=40, cmap='plasma', alpha=0.3)

# Plot the explicit Magnetic Field Lines (Isolines of Psi)
# Using a log-spaced layout or dense linear levels to capture near and far fields cleanly
field_lines = ax.contour(R, Z, Psi, levels=35, colors='#1a252c', linewidths=1.0)
ax.clabel(field_lines, inline=True, fmt='%.3f', fontsize=8, inline_spacing=4)

# Draw a bold cross-section of the flat uniform disk coil winding space
ax.plot([a, b], [z_prime, z_prime], color='#ff4500', linewidth=8, label='Disk Coil Cross-Section', zorder=10)
ax.plot([a, b], [z_prime, z_prime], color='white', linewidth=1.5, linestyle=':', zorder=11)

# Annotate current flow direction convention (Out of page on this side)
ax.scatter([a + (b - a) / 2], [z_prime], color='white', edgecolor='#ff4500', s=100, marker='o', zorder=12)
ax.scatter([a + (b - a) / 2], [z_prime], color='#ff4500', s=15, marker='.', zorder=13)

ax.set_xlabel('Radial Position r [m]')
ax.set_ylabel('Axial Position z [m]')
ax.set_title(r'Magnetic Field Lines $\Psi(r,z) = r A_\theta$ for Annular Disk Winding', fontsize=12, pad=15)
ax.legend(loc='upper right')
ax.grid(True, linestyle=':', alpha=0.4)

# Set clean window view boundaries
ax.set_xlim(0, 2.0)
ax.set_ylim(0, 2.5)

plt.show()
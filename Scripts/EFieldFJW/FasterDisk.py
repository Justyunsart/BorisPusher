import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from numba import njit, prange
from matplotlib.colors import LogNorm

# Constants
Q = 1e-11  # Coulomb
a = 0.25  # Disk inner radius (m)
b = 1.0  # Disk outer radius (m)
Sigma = Q / (np.pi * (b ** 2 - a ** 2))  # charge density C/m^2
prefactor = Sigma / (4 * np.pi * epsilon_0)

# Integration resolution
Nr = 100
Ntheta = 100
r_vals = np.linspace(a, b, Nr)
theta_vals = np.linspace(0, 2 * np.pi, Ntheta)
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
    Nr = len(r_vals)
    Ntheta = len(theta_vals)
    Nrho = len(rho_vals)
    Nz = len(z_vals)

    for i in prange(Nrho):
        rho = rho_vals[i]
        for j in range(Nz):
            z = z_vals[j]
            Erho_sum = 0.0
            Ez_sum = 0.0

            # Precompute cos and sin for all theta values
            cos_theta = np.cos(theta_vals)
            sin_theta = np.sin(theta_vals)

            # Precompute r * cos(theta) and r * sin(theta)
            for m in range(Nr):
                r = r_vals[m]
                dx = rho - r * cos_theta
                dy = -r * sin_theta
                dz = z

                # Calculate denominator
                Denom = (dx**2 + dy**2 + dz**2) ** 1.5 + 1e-20  # prevent zero division
                dA = r * dr * dtheta

                # Update sums
                Erho_sum += np.sum(dx / Denom) * dA
                Ez_sum += np.sum(dz / Denom) * dA

            E_rho[j, i] = prefactor * Erho_sum
            E_z[j, i] = prefactor * Ez_sum

# Calculate the field and total field magnitude
compute_fields(E_rho, E_z, rho_vals, z_vals, r_vals, theta_vals, dr, dtheta)
E_mag = np.sqrt(E_rho**2 + E_z**2)

# Plot
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(fr'Uniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20)

# Streamplot
c1 = axs[0, 0].streamplot(RHO, Z, E_rho, E_z, color=np.sqrt(E_rho**2 + E_z**2), cmap='plasma', density=1.2)
fig.colorbar(c1.lines, ax=axs[0, 0], label='$|\\vec{E}|$ Field Magnitude (V/m)')

# Create a pcolormesh with logarithmic normalization
c2 = axs[0, 1].pcolormesh(RHO, Z, E_mag, norm=LogNorm(), cmap='plasma')
cbar = fig.colorbar(c2, ax=axs[0, 1])
cbar.set_label('Log $|\\vec{E}|$ Field Magnitude (V/m)')

# Draw a solid line on the plots
x_values = [a, b]
y_values = [0, 0]
axs[0, 0].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0, 1].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0, 0].set_xlabel(r'Radial Distance, $\rho$ (m)')
axs[0, 0].set_ylabel(r'Axial Distance, $z$ (m)')
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
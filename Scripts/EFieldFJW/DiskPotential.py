import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from numba import njit, prange
from matplotlib.colors import LogNorm

# Constants
Q = 1e-11 # Couloumb
# a = 0.25 # Disk inner radius (m)
a = 0.01 # Disk inner radius (m)
b = 1.0 # Disk outer radius (m)
sigma = Q / (np.pi * (b ** 2 - a ** 2)) # charge density C/m^2
prefactor = sigma / (4 * np.pi * epsilon_0)

# integration grid
Nr = 200
Ntheta = 200
r_vals = np.linspace(a, b, Nr)
theta_vals = np.linspace(0, 2*np.pi, Ntheta)
dr = r_vals[1] - r_vals[0]
d_theta = theta_vals[1] - theta_vals[0]

# observation grid
rho_vals = np.linspace(0.01, 1.5, 200)  # meters
z_vals = np.linspace(0.01, 1, 200)    # meters
RHO, Z = np.meshgrid(rho_vals, z_vals)
Phi = np.zeros_like(RHO) #

@njit(parallel=True)
def compute_potential(Phi, rho_vals, z_vals, r_vals, theta_vals, dr, d_theta, prefactor):
    for i in prange(len(rho_vals)):
        for j in prange(len(z_vals)):
            rho = rho_vals[i]
            z = z_vals[j]
            Phi_sum = 0.0

            for m in range(len(r_vals)):
                r = r_vals[m]
                for n in range(len(theta_vals)):
                    theta = theta_vals[n]
                    dx = rho - r * np.cos(theta_vals[n])
                    dy = -r * np.sin(theta_vals[n])
                    dz = z
                    Denom = (dx * dx + dy * dy + dz * dz) ** 0.5 + 1e-20  # prevent zero division
                    dA = r * dr * d_theta
                    Phi_sum += dA / Denom
            Phi[j, i] = prefactor * Phi_sum

# Compute electric field from gradient
compute_potential(Phi, rho_vals, z_vals, r_vals, theta_vals, dr, d_theta, prefactor)

# Compute grid spacing
d_rho = rho_vals[1] - rho_vals[0]
d_z = z_vals[1] - z_vals[0]
dPhi_drho, dPhi_dz = np.gradient(Phi, d_rho, d_z, edge_order=2)
E_rho = -dPhi_drho
E_z = -dPhi_dz
E_mag = np.sqrt(E_rho**2 + E_z**2)

# plt.figure(figsize=(6, 5))
# cp = plt.contourf(RHO, Z, Phi, levels=50, cmap='viridis')
# plt.colorbar(cp, label='Potential (V)')
# plt.xlabel('ρ (m)')
# plt.ylabel('z (m)')
# plt.title('Electric Potential from Annular Disk')
# plt.tight_layout()
# plt.show()

# step = 10
# plt.figure(figsize=(6, 5))
# plt.contourf(RHO, Z, E_mag, levels=50, cmap='inferno', norm=LogNorm())
# plt.colorbar(label='|E| (V/m)')
# plt.quiver(
#     RHO[::step, ::step], Z[::step, ::step],
#     E_rho[::step, ::step], E_z[::step, ::step],
#     color='white'
# )
# plt.xlabel('ρ (m)')
# plt.ylabel('z (m)')
# plt.title('Electric Field Vectors from Annular Disk')
# plt.tight_layout()
# plt.show()

# Plot potential
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(fr'Uniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20)

c1 = axs[0,0].streamplot(RHO, Z, E_rho, E_z, color=np.sqrt(E_rho**2 + E_z**2), cmap='plasma', density=1.2)
fig.colorbar(c1.lines, ax=axs[0,0], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Create a pcolormesh with logarithmic normalization
c2 = axs[0,1].pcolormesh(RHO, Z, E_mag, norm=LogNorm(), cmap='plasma')
# fig.colorbar(np.log(E_mag), ax=axs[0,1], label='$|\\vec{E}|$ Field Magnitude (V/m)')
# Add a colorbar
cbar = fig.colorbar(c2, ax=axs[0,1])
cbar.set_label('Log $|\\vec{E}|$ Field Magnitude (V/m)')
# Draw a solid line on the plots
x_values = [a, b]
y_values = [0, 0]
axs[0,0].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
axs[0,1].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
#
# plt.show()
# # plt.figure(figsize=(6, 5))
# # cp = plt.contourf(RHO*100, Z*100, V, levels=50, cmap='viridis')
# # plt.colorbar(cp, label='Potential (V)')
# # plt.xlabel('ρ (cm)')
# # plt.ylabel('z (cm)')
# # plt.title('Electric Potential from Charged Annular Disk')
# # plt.tight_layout()
# #
# # # Plot electric field magnitude
# # E_mag = np.sqrt(E_rho**2 + E_z**2)
# # plt.figure(figsize=(6, 5))
# # cp = plt.contourf(RHO*100, Z*100, E_mag, levels=50, cmap='inferno')
# # plt.colorbar(cp, label='|E| (V/m)')
# # plt.xlabel('ρ (cm)')
# # plt.ylabel('z (cm)')
# # plt.title('Electric Field Magnitude from Annular Disk')
# plt.tight_layout()
# plt.show()

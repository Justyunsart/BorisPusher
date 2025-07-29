import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0
from scipy.special import ellipk, ellipe
from scipy.integrate import quad

# Constants
Q = 10**-11
a = 0.25      # Inner radius [m]
b = 1.0      # Outer radius [m]
sigma_denominator = np.pi*(b**2 -a**2)
sigma = Q/sigma_denominator  # C/m^2
print(sigma)
# sigma = 1e-6  # C/m^2

# Elliptic modulus function
def k_squared(R, rho, z):
    return 4 * R * rho / ((R + rho)**2 + z**2)

# Integrand for E_z
def integrand_Ez(R, rho, z):
    k2 = k_squared(R, rho, z)
    k = np.sqrt(k2)
    denom = ((R + rho)**2 + z**2)**(1.5)
    return R * ellipk(k2) / denom

# Integrand for E_rho
def integrand_Erho(R, rho, z):
    k2 = k_squared(R, rho, z)
    if k2 >= 1.0:
        return 0  # avoid singularity
    k = np.sqrt(k2)
    denom = ((R + rho)**2 + z**2)**(1.5)
    factor = ellipe(k2) / (1 - k2) - ellipk(k2)
    return R * factor / denom

# Compute E_z
def Ez(rho, z):
    integral, _ = quad(integrand_Ez, a, b, args=(rho, z), limit=200)
    return 2 * sigma * z * integral / epsilon_0

# Compute E_rho
def Erho(rho, z):
    integral, _ = quad(integrand_Erho, a, b, args=(rho, z), limit=200)
    return 2 * sigma * integral / epsilon_0

# Plot at fixed z and varying rho
z_values = [0.01, 0.05, 0.1, 0.5]
rho = np.linspace(0, 1.5, 300)

fig, axs = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

for z in z_values:
    Ez_vals = np.array([Ez(r, z) for r in rho])
    Erho_vals = np.array([Erho(r, z) for r in rho])
    axs[0].plot(rho*1000, Ez_vals, label=f'z = {z:.2f} m')
    axs[1].plot(rho*1000, Erho_vals, label=f'z = {z:.2f} m')

axs[0].set_ylabel(r'$E_z$ (V/m)')
axs[1].set_ylabel(r'$E_\rho$ (V/m)')
axs[1].set_xlabel(r'$\rho$ (mm)')
axs[0].set_title('Electric Field Components of an Annular Disk')
for ax in axs:
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0, pi
from scipy.integrate import quad

from EFieldFJW.ringEfield import rho_vals

# Constants
sigma = 1e-6    # C/m^2
a = 0.5         # Inner radius of disk (m)
b = 1.0      # Outer radius of disk (m)

# Observation points
z_vals = [0.01, 0.05, 0.1, 0.5]            # axial positions to evaluate
rho_vals = np.linspace(0.01, 0.5, 200)     # radial axis (avoid 0)

# Precompute values for far-field approximation
prefactor = sigma / (4 * epsilon_0)
delta_b2 = b**2 - a**2
delta_b4 = b**4 - a**4

# Exact electric field components
def E_exact_components(rho, z):
    def integrand_Ez(rp, phi):
        denom = (rho**2 + rp**2 - 2 * rho * rp * np.cos(phi) + z**2)**(3/2)
        return z * rp / denom

    def integrand_Erho(rp, phi):
        denom = (rho**2 + rp**2 - 2 * rho * rp * np.cos(phi) + z**2)**(3/2)
        return (rho - rp * np.cos(phi)) * rp / denom

    # Integrate over φ and r'
    def Ez_integral(rp): return quad(integrand_Ez, 0, 2*np.pi, args=(rp))[0]
    def Erho_integral(rp): return quad(integrand_Erho, 0, 2*np.pi, args=(rp))[0]

    Ez = sigma / (4 * pi * epsilon_0) * quad(lambda rp: Ez_integral(rp), a, b)[0]
    Erho = sigma / (4 * pi * epsilon_0) * quad(lambda rp: Erho_integral(rp), a, b)[0]

    return Erho, Ez

# Storage
fields_approx = {'Erho': {}, 'Ez': {}}
fields_exact = {'Erho': {}, 'Ez': {}}

# Loop over rho values
for rho in rho_vals:
    Erho_approx = []
    Ez_approx = []
    Erho_exact = []
    Ez_exact = []

    for z in z_vals:
        R = np.sqrt(rho**2 + z**2)

        # Far-field approximation
        E_rho_ff = prefactor * (delta_b2 * rho / R**3 + 3 * delta_b4 * z * rho / (4 * R**5))
        E_z_ff = prefactor * (delta_b2 * z / R**3 + delta_b4 * (3 * z**2 - R**2) / (4 * R**5))

        Erho_approx.append(E_rho_ff)
        Ez_approx.append(E_z_ff)

        # Exact value
        Erho_ex, Ez_ex = E_exact_components(rho, z)
        Erho_exact.append(Erho_ex)
        Ez_exact.append(Ez_ex)

    fields_approx['Erho'][rho] = np.array(Erho_approx)
    fields_approx['Ez'][rho] = np.array(Ez_approx)
    fields_exact['Erho'][rho] = np.array(Erho_exact)
    fields_exact['Ez'][rho] = np.array(Ez_exact)

# --- Plotting ---
plt.figure(figsize=(12, 6))

# Plot E_rho
plt.subplot(1, 2, 1)
for rho in rho_vals:
    plt.plot(z_vals, fields_exact['Erho'][rho], label=fr'Exact, $\rho = {rho:.2f}$ m', linestyle='-')
    plt.plot(z_vals, fields_approx['Erho'][rho], label=fr'Approx, $\rho = {rho:.2f}$ m', linestyle='--')
plt.title(r'Radial Field $E_\rho(z)$')
plt.xlabel(r'$z$ (m)')
plt.ylabel(r'$E_\rho$ (V/m)')
plt.grid(True)
plt.legend()

# Plot E_z
plt.subplot(1, 2, 2)
for rho in rho_vals:
    plt.plot(z_vals, fields_exact['Ez'][rho], label=fr'Exact, $\rho = {rho:.2f}$ m', linestyle='-')
    plt.plot(z_vals, fields_approx['Ez'][rho], label=fr'Approx, $\rho = {rho:.2f}$ m', linestyle='--')
plt.title(r'Axial Field $E_z(z)$')
plt.xlabel(r'$z$ (m)')
plt.ylabel(r'$E_z$ (V/m)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

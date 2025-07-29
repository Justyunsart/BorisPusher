# Attempt to solve for the analytic equations
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0, pi
from scipy.integrate import quad

# Constants
Q = 1e-11    # Surface charge density (C/m^2)
a = 0.25         # Inner radius (m)
b = 1.0        # Outer radius (m)
sigma = np.divide(Q, (np.pi(b**2 - a**2)))    # Surface charge density (C/m^2)

# Observation points
rho_vals = np.linspace(0.001, 1.5, 400)   # Radial positions (avoid 0)
# z_vals = [0.01, 0.05, 0.1, 0.5]           # Fixed axial positions
z_vals = [0.01, 0.05, 0.1, 0.5]           # Fixed axial positions

# Precompute constants for far-field approximation
prefactor = sigma / (4 * epsilon_0)
delta_b2 = b**2 - a**2
delta_b4 = b**4 - a**4

# Exact electric field components
def E_exact_components(rho, z):
    def integrand_Ez(phi, rp):
        denom = (rho**2 + rp**2 - 2 * rho * rp * np.cos(phi) + z**2)**(3/2)
        return z * rp / denom

    def integrand_Erho(phi, rp):
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

# Loop over fixed z values
for z in z_vals:
    Erho_approx = []
    Ez_approx = []
    Erho_exact = []
    Ez_exact = []

    for rho in rho_vals:
        R = np.sqrt(rho**2 + z**2)

        # Far-field approximation
        E_rho_ff = prefactor * (delta_b2 * rho / R**3 + 3 * delta_b4 * z * rho / (4 * R**5))
        E_z_ff = prefactor * (delta_b2 * z / R**3 + delta_b4 * (3 * z**2 - R**2) / (4 * R**5))

        Erho_approx.append(E_rho_ff)
        Ez_approx.append(E_z_ff)

        # Exact values
        Erho_ex, Ez_ex = E_exact_components(rho, z)
        Erho_exact.append(Erho_ex)
        Ez_exact.append(Ez_ex)

    fields_approx['Erho'][z] = np.array(Erho_approx)
    fields_approx['Ez'][z] = np.array(Ez_approx)
    fields_exact['Erho'][z] = np.array(Erho_exact)
    fields_exact['Ez'][z] = np.array(Ez_exact)

# --- Plotting ---
plt.figure(figsize=(12, 6))

# Plot E_rho
plt.subplot(1, 2, 1)
for z in z_vals:
    plt.plot(rho_vals, fields_exact['Ez'][z], label=fr'Exact, $z = {z:.2f}$ m', linestyle='-')
    # plt.plot(rho_vals, fields_approx['Ez'][z], label=fr'Approx, $z = {z:.2f}$ m', linestyle='--')
plt.title(r'Axial Field $E_z(\rho)$')
plt.xlabel(r'$\rho$ (m)')
plt.ylabel(r'$E_z$ (V/m)')
plt.grid(True)
plt.legend()

# Plot E_z
plt.subplot(1, 2, 2)
for z in z_vals:
    plt.plot(rho_vals, fields_exact['Erho'][z], label=fr'Exact, $z = {z:.2f}$ m', linestyle='-')
    # plt.plot(rho_vals, fields_approx['Erho'][z], label=fr'Approx, $z = {z:.2f}$ m', linestyle='--')
plt.title(r'Radial Field $E_\rho(\rho)$')
plt.xlabel(r'$\rho$ (m)')
plt.ylabel(r'$E_\rho$ (V/m)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

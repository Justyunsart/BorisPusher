import numpy as np
import matplotlib.pyplot as plt
from scipy.special import ellipk, ellipe

# Constants and parameters
epsilon_0 = 8.854187817e-12  # Vacuum permittivity (F/m)
Q = 1e-9  # Total charge on the ring (C)
a = 1.0   # Ring radius (m)
z = 0.0001  # Slightly above the ring plane

# Radial coordinates (rho = |x| along x-axis, y = 0)
rho = np.linspace(0.01, 2*a, 1000)  # Avoid rho=0 exactly to prevent division by zero

# Elliptic integral parameter
k_sq = 4 * a * rho / ((a + rho)**2 + z**2)
k = np.sqrt(k_sq)

# Elliptic integrals
K = ellipk(k_sq)
E = ellipe(k_sq)

# Common factor
R = np.sqrt((a + rho)**2 + z**2)
denom = (a - rho)**2 + z**2

# Electric field components
Erho = (Q / (4 * np.pi**2 * epsilon_0)) * (z / (rho * R)) * (
    -K + ((a**2 + rho**2 + z**2) / denom) * E
)

#Ez = ((Q / (4 * np.pi**2 * epsilon_0)) * (1 / R) *
#      (K + ((a**2 - rho**2 - z**2) / denom) * E))
Ez = ((Q / (4 * np.pi**2 * epsilon_0)) * (1 / R) *
      (K + ((a**2 - rho**2 - z**2) / denom) * E))
# Plotting
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(rho, np.log(Erho), label=r'$E_\rho$', color='tab:blue')
plt.axvline(a, color='gray', linestyle='--', label='Ring Radius')
plt.xlabel('Radial Distance ρ (m)')
plt.ylabel('E-field (V/m)')
plt.title(r'$E_\rho$ vs ρ (at $z = 0.0001$ m)')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(rho, Ez, label=r'$E_z$', color='tab:red')
plt.axvline(a, color='gray', linestyle='--', label='Ring Radius')
plt.xlabel('Radial Distance ρ (m)')
plt.ylabel('E-field (V/m)')
plt.title(r'$E_z$ vs ρ (at $z = 0.0001$ m)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

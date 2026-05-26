import numpy as np
from scipy.constants import mu_0
from scipy.special import ellipk, ellipe
import matplotlib.pyplot as plt


# ============================================================
# Exact B-Field of ONE Circular Loop (Direct Biot-Savart)
# ============================================================

def B_loop_local(rho, z, R, I):
    """Computes exact local Brho and Bz for a single loop using elliptic integrals."""
    if rho < 1e-10:
        # On-axis exact solution
        Bz = mu_0 * I * R ** 2 / (2 * (R ** 2 + z ** 2) ** 1.5)
        return 0.0, Bz

    # Modulus parameter k^2
    k2 = 4 * R * rho / ((R + rho) ** 2 + z ** 2)
    k2 = np.clip(k2, 0, 1 - 1e-12)

    K = ellipk(k2)
    E = ellipe(k2)

    denom_common = 2 * np.pi * np.sqrt((R + rho) ** 2 + z ** 2)
    denom_singular = (R - rho) ** 2 + z ** 2

    # Avoid division by zero exactly at the wire filament
    if denom_singular < 1e-12:
        return 0.0, 0.0

    # Brho component
    Brho = (mu_0 * I * z / (rho * denom_common)) * (
            ((R ** 2 + rho ** 2 + z ** 2) / denom_singular) * E - K
    )

    # Bz component
    Bz = (mu_0 * I / denom_common) * (
            ((R ** 2 - rho ** 2 - z ** 2) / denom_singular) * E + K
    )

    return Brho, Bz


def B_coil_global(r_global, coil):
    """Transforms global coordinates to local coil coordinates, computes cumulative B, and transforms back."""
    # Transform global point to local coil frame
    r_local = coil["R"] @ (r_global - coil["center"])
    rho = np.linalg.norm(r_local[:2])
    z = r_local[2]

    # Radii distribution for multi-turn
    Rs = np.linspace(coil["a"], coil["b"], coil["turns"])

    B_rho_total = 0.0
    B_z_total = 0.0

    for R in Rs:
        Br, Bz = B_loop_local(rho, z, R, coil["I"])
        B_rho_total += Br
        B_z_total += Bz

    # Note: No division by coil["turns"] here so N_turns scales cumulatively!

    # Reconstruct local B vector
    if rho > 1e-10:
        cos_phi = r_local[0] / rho
        sin_phi = r_local[1] / rho
        B_local = np.array([B_rho_total * cos_phi, B_rho_total * sin_phi, B_z_total])
    else:
        B_local = np.array([0.0, 0.0, B_z_total])

    # Rotate local B vector back to global frame
    return coil["R"].T @ B_local
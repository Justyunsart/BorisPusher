"""
Fast 2-D magnetic field solver for two multi-turn coils
Computes the magnetic field from Biot Savart solution and elliptic integrals

Features
--------
- Disable one coil by entering "false" in the "main" subroutine descriptor
- Multi-turn annular coils
- Field-line visualization
- Contour plots and lineouts
- background for contour plots is commented "off" line 143, et.seq.

Author: F. J. Wessel
Date: June 2026
"""

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

    # Reconstruct local B vector
    if rho > 1e-10:
        cos_phi = r_local[0] / rho
        sin_phi = r_local[1] / rho
        B_local = np.array([B_rho_total * cos_phi, B_rho_total * sin_phi, B_z_total])
    else:
        B_local = np.array([0.0, 0.0, B_z_total])

    # Rotate local B vector back to global frame
    return coil["R"].T @ B_local


# ============================================================
# Plotting Implementation
# ============================================================

def create_coil(center, radius_in, radius_out, turns, current, enabled=True):
    """Helper to define a coil dictionary with an identity rotation matrix and toggle status."""
    return {
        "center": np.array(center),
        "R": np.eye(3),  # Coils aligned with the Z-axis
        "a": radius_in,
        "b": radius_out,
        "turns": turns,
        "I": current,
        "enabled": enabled  # Control whether the coil is computed/drawn
    }


if __name__ == "__main__":
    # Updated Dimensions: ID = 0.1 -> radius_in = 0.05 | OD = 0.8 -> radius_out = 0.40
    coil1 = create_coil(center=[0.0, 0.0, -0.1], radius_in=0.074, radius_out=0.076, turns=10, current=1e5, enabled=True)
    coil2 = create_coil(center=[0.0, 0.0, 0.1], radius_in=0.074, radius_out=0.076, turns=10, current=1e5, enabled=False)
    coils = [coil1, coil2]

    # Expanded grid range to perfectly fit the new 0.8m Outer Diameter
    num_points = 100
    x_range = np.linspace(-0.6, 0.6, num_points)
    z_range = np.linspace(-0.6, 0.6, num_points)
    X, Z = np.meshgrid(x_range, z_range)

    # Initialize arrays to hold the field components
    Bx = np.zeros_like(X)
    Bz = np.zeros_like(Z)

    # Compute the total B-field at each grid point
    for i in range(num_points):
        for j in range(num_points):
            r_global = np.array([X[i, j], 0.0, Z[i, j]])  # Y = 0 slice
            B_total = np.zeros(3)

            for coil in coils:
                if coil["enabled"]:  # Only add field contribution if the coil is active
                    B_total += B_coil_global(r_global, coil)

            Bx[i, j] = B_total[0]
            Bz[i, j] = B_total[2]

    # Calculate the total magnitude of the B-field (in Tesla)
    B_magnitude = np.sqrt(Bx ** 2 + Bz ** 2)

    # Create the plot
    plt.figure(figsize=(9, 7))

    # # 1. Plot the field magnitude as a background contour map
    # levels = np.linspace(0, np.percentile(B_magnitude, 95), 50)  # Cap max to avoid filament singularities
    # contour = plt.contourf(X, Z, B_magnitude, levels=levels, cmap="viridis", extend='max')
    # cbar = plt.colorbar(contour)
    # cbar.set_label("Magnetic Field Strength $|B|$ (Tesla)", rotation=270, labelpad=15)

    # 2. Plot the magnetic field lines using streamplot
    plt.streamplot(X, Z, Bx, Bz, color="purple", linewidth=1.0, density=1.2, arrowstyle="->", arrowsize=1.0)

    # 3. Mark the cross-sections of the coil wires ONLY if they are enabled
    legend_added = False
    for coil in coils:
        if not coil["enabled"]:
            continue  # Completely skip rendering if disabled

        z_c = coil["center"][2]
        label = "Coil Cross-section" if not legend_added else ""
        legend_added = True

        plt.plot([coil["a"], coil["b"]], [z_c, z_c], color="red", linewidth=4, label=label)
        plt.plot([-coil["a"], -coil["b"]], [z_c, z_c], color="red", linewidth=4)

    plt.title("Magnetic Field Lines & Intensity (X-Z Plane)")
    plt.xlabel("X Coordinate (m)")
    plt.ylabel("Z Coordinate (m)")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.legend(loc="upper right")
    plt.axis("equal")

    plt.show()
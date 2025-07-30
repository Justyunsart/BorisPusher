import numpy as np
from numba import njit, prange
from scipy.constants import epsilon_0

def compute_washer_potential(rho_vals, z_vals, Q, inner_r, outer_r, res=400):
    """
    grid: array, (2,n): either one point or a meshgrid, representing (rho, phi, zeta) to calc at.
    """
    sigma = Q / (np.pi * (outer_r ** 2 - inner_r ** 2))  # charge density C/m^2
    prefactor = sigma / (4 * np.pi * epsilon_0)

    # Create a meshgrid for r and theta (used in integration)
    r_vals = np.linspace(inner_r, outer_r, res)
    theta_vals = np.linspace(0, 2 * np.pi, res)
    dr = r_vals[1] - r_vals[0]
    dtheta = theta_vals[1] - theta_vals[0]

    r, theta = np.meshgrid(r_vals, theta_vals, indexing='ij')  # shape: (Nr, Ntheta)

    # Precompute differential area element dA
    dA = r * dr * dtheta  # shape: (Nr, Ntheta)

    # Precompute x and y coordinates of source points in the integration plane
    x_src = r * np.cos(theta)  # shape: (Nr, Ntheta)
    y_src = r * np.sin(theta)

    Phi = np.empty(rho_vals)
    for i in range(len(rho_vals)):
        for j in range(len(z_vals)):
            rho = rho_vals[i]
            z = z_vals[j]

            # Distance from (rho, 0, z) to each source point (x_src, y_src, 0)
            dx = rho - x_src
            dy = -y_src
            dz = z

            Denom = np.sqrt(dx**2 + dy**2 + dz**2) + 1e-20  # avoid division by zero

            integrand = dA / Denom  # shape: (Nr, Ntheta)

            Phi[j, i] = prefactor * np.sum(integrand)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from numba import njit, prange
    from matplotlib.colors import LogNorm
    import textwrap

    # Constants
    Q = 1e-11  # Couloumb
    a = 0.25  # Disk inner radius (m)
    b = 1.0  # Disk outer radius (m)
    sigma = Q / (np.pi * (b ** 2 - a ** 2))  # charge density C/m^2
    prefactor = sigma / (4 * np.pi * epsilon_0)

    # integration grid
    Nr = 400
    Ntheta = 400
    r_vals = np.linspace(a, b, Nr)
    theta_vals = np.linspace(0, 2 * np.pi, Ntheta)
    dr = r_vals[1] - r_vals[0]
    dtheta = theta_vals[1] - theta_vals[0]

    # Field grid
    rho_vals = np.linspace(0.01, 1.5, 200)  # meters
    z_vals = np.linspace(-0.25, 1, 200)  # meters
    RHO, Z = np.meshgrid(rho_vals, z_vals)
    E_rho = np.zeros_like(RHO)
    E_z = np.zeros_like(Z)


    # Compute electric field from gradient
    #(rho, z, Q, inner_r, outer_r, res=400)
    Phi = compute_washer_potential(RHO, Z, Q, a, b, 400)

    # Compute grid spacing
    d_rho = rho_vals[1] - rho_vals[0]
    d_z = z_vals[1] - z_vals[0]
    dPhi_dz, dPhi_drho = np.gradient(Phi, d_rho, d_z, edge_order=1)  # note the rho, z order for Phi
    E_rho = -dPhi_drho
    E_z = -dPhi_dz
    E_mag = np.sqrt(E_rho ** 2 + E_z ** 2)

    # Plot potential
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    title = fr"Electric Field Calculated from a Scalar Potential for a Uniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C"
    wrapped = "\n".join(textwrap.wrap(title, width=60))
    # fig.suptitle(fr'Electric Field Calculated from a Scalar Potential for a \nUniformly-Charged Washer (radii a, b = {a}, {b} m), Centered at (X, Y, 0), $Q = 10^{{-11}}$ C', fontsize=20))
    fig.suptitle(wrapped, fontsize=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])  # reserve space for suptitle

    c1 = axs[0, 0].streamplot(RHO, Z, E_rho, E_z, color=np.sqrt(E_rho ** 2 + E_z ** 2), cmap='plasma', density=1.2)
    fig.colorbar(c1.lines, ax=axs[0, 0], label='$|\\vec{E}|$ Field Magnitude (V/m)')
    # Create a pcolormesh with logarithmic normalization
    c2 = axs[0, 1].pcolormesh(RHO, Z, E_mag, norm=LogNorm(), cmap='plasma')
    # fig.colorbar(np.log(E_mag), ax=axs[0,1], label='$|\\vec{E}|$ Field Magnitude (V/m)')
    # Add a colorbar
    cbar = fig.colorbar(c2, ax=axs[0, 1])
    cbar.set_label('Log $|\\vec{E}|$ Field Magnitude (V/m)')
    # Draw a solid line on the plots
    x_values = [a, b]
    y_values = [0, 0]
    axs[0, 0].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
    axs[0, 1].plot(x_values, y_values, color='green', linewidth=6, label="Charged Conductor")
    axs[0, 0].set_xlabel(r'Radial Distance, $\rho$ (m)')
    axs[0, 0].set_ylabel(r'Axial Distance, $z$ (m)')
    axs[0, 1].set_xlabel(r'Radial Distance, $\rho$ (m)')
    axs[0, 1].set_ylabel(r'Axial Distance, $z$ (m)')
    axs[0, 0].grid(True)
    axs[0, 0].legend()
    axs[0, 1].legend()
    axs[0, 1].grid(True)
    axs[0, 0].set_title('$\\vec{E}$ Field Streamlines')
    axs[0, 1].set_title('$\\vec{E}$ Field Magnitude')
    #
    rho1 = 100
    rho2 = 180
    z_lo_min = 0.01
    z_lo_vals = [z_lo_min, 5 * z_lo_min, 10 * z_lo_min, 50 * z_lo_min]
    for z_lineout in z_lo_vals:
        lineout_val = np.argmin(np.abs(z_vals - z_lineout))
        closest_value = z_vals[lineout_val]
        index = lineout_val
        axs[1, 0].plot(rho_vals, E_rho[lineout_val, :], label=fr'{z_lineout} mm')
        axs[1, 1].plot(rho_vals, E_z[lineout_val, :], label=fr'{z_lineout} mm')
        axs[1, 0].legend()
        axs[1, 1].legend()
    axs[1, 0].set_title('Radial Line-Outs for $\\vec{E}_{\\rho}$ Field at z = ')
    axs[1, 0].set_xlabel(r'radial distance, $\rho$ (m)')
    axs[1, 0].grid(True)
    axs[1, 0].set_ylabel('Electric Field (V/m)')
    axs[1, 1].set_title('Radial Line-Outs for $\\vec{E}_z$ Field  at z = ')
    axs[1, 1].set_xlabel(r'Radial Distance, $\rho$ (m)')
    axs[1, 1].set_ylabel('Electric Field  (V/m)')
    axs[1, 1].grid(True)

    plt.tight_layout()
    plt.show()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as m
# Physical constants and parameters
epsilon_0 = 8.854e-12  # Vacuum permittivity (F/m)
Q = 1e-9               # Total charge on the ring (Coulombs)
a = 1.0                # Radius of the ring (meters)
lambda_ = Q / (2 * np.pi * a)  # Linear charge density

# Define the electric field components
def integrand_Er(theta, r, z):
    D = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return (r - a * np.cos(theta)) / D**3

def integrand_Ez(theta, r, z):
    D = np.sqrt(r**2 + a**2 - 2 * a * r * np.cos(theta) + z**2)
    return 1 / D**3

def compute_field(r, z):
    theta = np.linspace(0, 2 * np.pi, 500)
    dtheta = theta[1] - theta[0]
    int_Er = np.sum(integrand_Er(theta, r, z)) * dtheta
    int_Ez = np.sum(integrand_Ez(theta, r, z)) * dtheta
    E_r = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * int_Er
    E_z = (1 / (4 * np.pi * epsilon_0)) * lambda_ * a * z * int_Ez
    return E_r, E_z

if __name__ == '__main__':

    # Grid setup in r-z plane
    r_vals = np.linspace(0.1, 2.0, 40)
    z_vals = np.linspace(-2.0, 2.0, 40)
    R, Z = np.meshgrid(r_vals, z_vals)

    # Compute field components
    E_r = np.zeros_like(R)
    E_z = np.zeros_like(Z)
    # E_m = np.zeros_like(Z)

    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            E_r[i, j], E_z[i, j] = compute_field(R[i, j], Z[i, j])

    # Compute field magnitude
    E_m = np.sqrt(E_r ** 2 + E_z ** 2)

    # Streamplot requires 2D Cartesian grid
    X = R
    Y = Z
    U = E_r
    V = E_z
    W = E_m

    cm = m.colors.LinearSegmentedColormap('viridis', 1024)

    # Plot streamlines
    # fig, ax = plt.subplots(figsize=(10, 6))
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    strm = axs[0,0].streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='plasma', density=1.2)

    contour = axs[0,1].contourf(X, Y, W, levels=50, cmap='plasma')
    c3 = axs[1,0].contourf(X, Y, U, levels=50, cmap='plasma')
    c4 = axs[1,1].contourf(X, Y, V, levels=50, cmap='plasma')
    # # Plot the ring in r-z plane (circular ring at z=0)
    # theta_ring = np.linspace(0, 2 * np.pi, 200)
    # ring_x = a * np.cos(theta_ring)
    # ring_y = a * np.sin(theta_ring)
    # ax.plot(ring_x, ring_y, 'r', linewidth=2, label='Ring of Charge')

    # Draw a solid line on the plot; define the x and y values, and plot the line
    x_values = [-1, 1]
    y_values = [0, 0]
    axs[0,0].plot(x_values, y_values, color='red', linewidth=4, label="Ring of Charge")

    # Labels and formatting
    axs[0,0].set_title('Electric Field Streamlines for a Charged Ring (2D slice)')
    axs[0,1].set_title('Electric Field Magnitude (2D slice)')
    axs[1,0].set_title('Er Contours (2D slice)')
    axs[1,1].set_title('Ez Contours (2D slice)')

    axs[0,0].set_xlabel('r (m)')
    axs[0,0].set_ylabel('z (m)')
    axs[0,0].legend()
    fig.colorbar(strm.lines, ax=axs[0,0], label='Electric Field Magnitude (a.u.)')
    fig.colorbar(contour, ax=axs[0,1], label='Electric Field Magnitude (a.u.)')
    fig.colorbar(c3, ax=axs[1,0], label='$E_r$ Magnitude (a.u.)')
    fig.colorbar(c4, ax=axs[1,1], label='$E_z$ Magnitude (a.u.)')
    axs[0,0].axis('equal')
    axs[0,0].grid(True)
    plt.tight_layout()
    plt.show()

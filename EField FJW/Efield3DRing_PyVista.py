import numpy as np
import pyvista as pv

#NOT SURE WHAT THIS IS PLOTTING

# Constants
k = 8.987551787e9  # Coulomb constant
R = 1.0            # Ring radius (meters)
Q = 1e-9           # Total charge (Coulombs)
N_ring = 200       # Number of point charges in ring
dq = Q / N_ring

# Discretize the ring (in xy-plane)
theta = np.linspace(0, 2 * np.pi, N_ring, endpoint=False)
ring_x = R * np.cos(theta)
ring_y = R * np.sin(theta)
ring_z = np.zeros_like(theta)

ring_points = np.vstack((ring_x, ring_y, ring_z)).T

# Grid definition
grid_res = 20
x = y = z = np.linspace(-2, 2, grid_res)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
Ex = np.zeros_like(X)
Ey = np.zeros_like(Y)
Ez = np.zeros_like(Z)

# Compute E-field at each grid point
for rx0, ry0, rz0 in ring_points:
    dx = X - rx0
    dy = Y - ry0
    dz = Z - rz0
    r2 = dx**2 + dy**2 + dz**2
    r3 = (r2 * np.sqrt(r2)) + 1e-20  # Avoid divide by zero

    Ex += k * dq * dx / r3
    Ey += k * dq * dy / r3
    Ez += k * dq * dz / r3

# Create a PyVista StructuredGrid
grid = pv.StructuredGrid()
grid.points = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
grid.dimensions = X.shape
grid["E"] = np.c_[Ex.ravel(), Ey.ravel(), Ez.ravel()]

# Define a source of seeds for streamlines (e.g., a sphere at center)
seed = pv.Sphere(radius=0.2, center=(0, 0, 0), theta_resolution=10, phi_resolution=10)

# Generate streamlines
streamlines = grid.streamlines_from_source(
    source=seed,
    vectors="E",
    integrator_type=45,  # Runge-Kutta 4/5
    integration_direction='both',
    max_time=5.0,
    # initial_step_length=0.1,
    initial_step_length=2,
    # step_unit='l',
    step_unit='cl', #either step unit gives same result
    terminal_speed=1e-5
)

# Create ring mesh
ring_curve = pv.Spline(ring_points, 100)

# Plotting
plotter = pv.Plotter()
plotter.add_mesh(streamlines.tube(radius=0.01), color="blue", name="streamlines")
plotter.add_mesh(ring_curve, color="red", line_width=4, name="charged_ring")
plotter.add_axes()
plotter.show_bounds(grid='front', location='outer', all_edges=True)
plotter.show(title="3D Electric Field Streamlines from Charged Ring")

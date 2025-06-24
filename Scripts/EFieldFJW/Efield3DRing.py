import numpy as np
import plotly.graph_objects as go

# Constants
k = 8.987551787e9  # Coulomb constant in N·m²/C²
R = 1.0            # Radius of the ring (m)
Q = 1e-9           # Total charge on the ring (C)
N_ring = 200       # Number of charge elements on the ring
N_grid = 7         # Grid resolution in each dimension

# Ring charge elements
theta = np.linspace(0, 2 * np.pi, N_ring, endpoint=False)
ring_x = R * np.cos(theta)
ring_y = R * np.sin(theta)
ring_z = np.zeros_like(theta)
dq = Q / N_ring

# Observation grid
grid_range = np.linspace(-2, 2, N_grid)
X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range)
Ex, Ey, Ez = np.zeros_like(X), np.zeros_like(Y), np.zeros_like(Z)

# Compute E-field at each point
for i in range(N_ring):
    rx = X - ring_x[i]
    ry = Y - ring_y[i]
    rz = Z - ring_z[i]
    r_squared = rx**2 + ry**2 + rz**2
    r_norm = np.sqrt(r_squared)
    r_cubed = r_squared * r_norm + 1e-20  # Add small term to avoid division by zero

    Ex += k * dq * rx / r_cubed
    Ey += k * dq * ry / r_cubed
    Ez += k * dq * rz / r_cubed

# Normalize for visualization
E_magnitude = np.sqrt(Ex**2 + Ey**2 + Ez**2)
Exn = Ex / (E_magnitude + 1e-20)
Eyn = Ey / (E_magnitude + 1e-20)
Ezn = Ez / (E_magnitude + 1e-20)

# Create 3D quiver plot
fig = go.Figure(data=go.Cone(
    x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
    u=Exn.flatten(), v=Eyn.flatten(), w=Ezn.flatten(),
    colorscale='Viridis', sizemode="absolute", sizeref=0.5,
    showscale=True
))

# Add ring as a 3D scatter
fig.add_trace(go.Scatter3d(
    x=ring_x, y=ring_y, z=ring_z,
    mode='lines',
    line=dict(color='red', width=6),
    name='Charged Ring'
))

# Set layout
fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        aspectratio=dict(x=1, y=1, z=1),
    ),
    title="Electric Field of a Charged Ring"
)

fig.show()

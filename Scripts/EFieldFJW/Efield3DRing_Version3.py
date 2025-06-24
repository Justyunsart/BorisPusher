import numpy as np
import plotly.graph_objects as go

# Constants
k = 8.99e9  # Coulomb constant (N·m²/C²)
Q = 1e-9    # Total charge on the ring (C)
R = 1.0     # Radius of the ring (m)

# Grid setup
grid_size = 8
x = np.linspace(-2, 2, grid_size)
y = np.linspace(-2, 2, grid_size)
z = np.linspace(-2, 2, grid_size)
X, Y, Z = np.meshgrid(x, y, z)

# Initialize field components
Ex = np.zeros_like(X)
Ey = np.zeros_like(Y)
Ez = np.zeros_like(Z)

# Discretize the ring into point charges
num_ring_points = 200
theta = np.linspace(0, 2*np.pi, num_ring_points)
ring_x = R * np.cos(theta)
ring_y = R * np.sin(theta)
ring_z = np.zeros_like(theta)
dq = Q / num_ring_points

# Compute electric field from each ring segment
for i in range(num_ring_points):
    rx = X - ring_x[i]
    ry = Y - ring_y[i]
    rz = Z - ring_z[i]
    r = np.sqrt(rx**2 + ry**2 + rz**2)
    r3 = np.where(r != 0, r**3, np.inf)
    Ex += k * dq * rx / r3
    Ey += k * dq * ry / r3
    Ez += k * dq * rz / r3

# Normalize vectors for visualization
magnitude = np.sqrt(Ex**2 + Ey**2 + Ez**2)
Ex /= magnitude
Ey /= magnitude
Ez /= magnitude

# Flatten arrays for Plotly
Xf = X.flatten()
Yf = Y.flatten()
Zf = Z.flatten()
U = Ex.flatten()
V = Ey.flatten()
W = Ez.flatten()

# Create 3D quiver plot
fig = go.Figure(data=go.Cone(
    x=Xf, y=Yf, z=Zf,
    u=U, v=V, w=W,
    sizemode="absolute",
    sizeref=0.5,
    showscale=False,
    colorscale='Blues'
))

# Add the ring of charge
fig.add_trace(go.Scatter3d(
    x=ring_x, y=ring_y, z=ring_z,
    mode='lines',
    line=dict(color='red', width=4),
    name='Ring of Charge'
))

fig.update_layout(
    title='3D Electric Field of a Ring of Charge',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        aspectmode='cube'
    ),
    showlegend=False
)

fig.show()
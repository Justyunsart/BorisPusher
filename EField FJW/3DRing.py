import numpy as np
import plotly.graph_objects as go

# Ring parameters
R = 1.0               # Radius
N = 200               # Number of points
theta = np.linspace(0, 2*np.pi, N)

# 3D ring coordinates (in XY plane)
x = R * np.cos(theta)
y = R * np.sin(theta)
z = np.zeros_like(x)

# Create 3D ring trace
ring_trace = go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines',
    line=dict(color='red', width=6),
    name='Charged Ring'
)

# Projection onto XY plane (z=0) – same as ring
xy_proj = go.Scatter3d(
    x=x, y=y, z=np.zeros_like(z),
    mode='lines',
    line=dict(color='lightblue', dash='dot'),
    name='XY Projection'
)

# Projection onto XZ plane (y=0)
xz_proj = go.Scatter3d(
    x=x, y=np.zeros_like(y), z=z,
    mode='lines',
    line=dict(color='green', dash='dot'),
    name='XZ Projection'
)

# Layout
layout = go.Layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        aspectratio=dict(x=1, y=1, z=0.5),
    ),
    title="3D Charged Ring with Projections",
    legend=dict(x=0.7, y=0.9)
)

# Combine traces
fig = go.Figure(data=[ring_trace, xy_proj, xz_proj], layout=layout)
fig.show()

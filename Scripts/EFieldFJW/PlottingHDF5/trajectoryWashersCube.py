import h5py
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Load trajectory data from HDF5 ---
# file_path = "data.hdf5"
# file_path = "data_new.hdf5"
file_path = "data_new2.hdf5"
with h5py.File(file_path, "r") as f:
    dset = f["src/position"][:]

# Handle structured or plain array
if dset.dtype.names is not None:
    df = pd.DataFrame({name: dset[name] for name in dset.dtype.names})
else:
    df = pd.DataFrame(dset, columns=["px", "py", "pz"])

# --- Parameters ---
a = 0.125   # inner radius of washer
b = 0.375   # outer radius of washer
c = 1.0   # cube width

# --- Washer generation ---
def make_washer(a, b, n_points=60, n_angles=60):
    r = np.linspace(a, b, n_points)
    theta = np.linspace(0, 2*np.pi, n_angles)
    R, Theta = np.meshgrid(r, theta)
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)
    Z = np.zeros_like(X)
    return X, Y, Z

def transform_coords(X, Y, Z, orientation, offset):
    if orientation == 'z+':   # xy plane at z=+c/2
        return X, Y, Z + offset
    elif orientation == 'z-': # xy plane at z=-c/2
        return X, Y, Z - offset
    elif orientation == 'x+': # yz plane at x=+c/2
        return Z + offset, X, Y
    elif orientation == 'x-': # yz plane at x=-c/2
        return -Z - offset, X, Y
    elif orientation == 'y+': # xz plane at y=+c/2
        return X, Z + offset, Y
    elif orientation == 'y-': # xz plane at y=-c/2
        return X, -Z - offset, Y

# --- Plot ---
fig = go.Figure()

# 1. Trajectory
fig.add_trace(go.Scatter3d(
    x=df["px"], y=df["py"], z=df["pz"],
    mode="lines",
    line=dict(color="blue", width=4),
    name="Trajectory"
))

# 2. Cube wireframe
cube_range = [-c, c]
for x in cube_range:
    for y in cube_range:
        fig.add_trace(go.Scatter3d(x=[x,x], y=[y,y], z=cube_range,
                                   mode="lines", line=dict(color="black")))
for x in cube_range:
    for z in cube_range:
        fig.add_trace(go.Scatter3d(x=[x,x], y=cube_range, z=[z,z],
                                   mode="lines", line=dict(color="black")))
for y in cube_range:
    for z in cube_range:
        fig.add_trace(go.Scatter3d(x=cube_range, y=[y,y], z=[z,z],
                                   mode="lines", line=dict(color="black")))

# 3. Washers on cube faces
X0, Y0, Z0 = make_washer(a, b)
for orient in ['x+','x-','y+','y-','z+','z-']:
    X, Y, Z = transform_coords(X0, Y0, Z0, orient, c)
    fig.add_surface(x=X, y=Y, z=Z, colorscale="Viridis", showscale=False, opacity=0.6)

# Final layout
fig.update_layout(
    title="Trajectory with Washers on Cube Faces",
    scene=dict(aspectmode="cube")
)

fig.show()

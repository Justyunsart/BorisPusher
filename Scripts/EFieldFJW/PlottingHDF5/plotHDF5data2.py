''''# Python program to create, read, plot data in an HDF5 file'''

import h5py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Read the dataset
with h5py.File('data.hdf5', 'r') as f:
        position_data = f['src/position'][:]

# Convert to DataFrame (assuming each entry is (x, y, z))
df = pd.DataFrame(position_data, columns=["x", "y", "z"])

fig = go.Figure()
# Scatter plot: x vs y, colored by z
fig = px.scatter_3d(
    df, x="x", y="y", z ="z",
    title="3D Scatter Plot of Position Data",
    # labels={"x": "X Position", "y": "Y Position", "color": "Z Position"},
    opacity=0.7
)

fig.show()
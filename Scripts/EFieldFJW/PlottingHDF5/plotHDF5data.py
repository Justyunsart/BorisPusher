''''# Python program to create, read, plot data in an HDF5 file'''

import numpy as np
import h5py
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Random numpy array
# arr = np.random.randn(1000)

# Creating datafile
# with h5py.File('test.hdf5', 'w') as f:
# with h5py.File('test.hdf5', 'w') as f:
#     dset = f.create_dataset("default", data = arr)

# Read the dataset
with h5py.File('data.hdf5', 'r') as f:
        position_data = f['src/position'][:]

# Convert to DataFrame (assuming each entry is (x, y, z))
df = pd.DataFrame(position_data, columns=["x", "y", "z"])

# # Minimum value
# print("Min=", min(position_data))
#
# # Maximum value
# print("Max=", max(position_data))
#
# # Values from index 0 to 15
# print("Data entries 0 - 15:", position_data[:15])

# Subplots
# fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Line Plot"))

# Histogram
# fig.add_trace(
#     go.Histogram(x=data, nbinsx=30, name="Histogram"),
#     row=1, col=1
# )
# Line chart
# fig.add_trace(
#     go.Scatter(y=data, name="Line Plot"),
#     row=1, col=2
# )
# Scatter plot: x vs y, colored by z
fig = px.scatter_3d(
    df, x="x", y="y", z ="z",
    title="3D Scatter Plot of Position Data",
    # labels={"x": "X Position", "y": "Y Position", "color": "Z Position"},
    opacity=0.7
)
fig.show()
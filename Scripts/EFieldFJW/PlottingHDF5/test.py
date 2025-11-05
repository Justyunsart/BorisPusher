''''# Python program to create, read, plot data in an HDF5 file'''

import h5py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Cube and Washer Parameters ---
I = 100 # kA
R = 0.5   # coil radius
c = 1.1  # cube half width
a = 0.125  # radius inner  of washer
b = 0.375  # radius outer of washer
Q = 1e-9 # coulombs

# Read the dataset
# with h5py.File('data.hdf5', 'r') as f:
#         position_data = f['src/position'][:]
#
# # Convert to DataFrame (assuming each entry is (x, y, z))
# df = pd.DataFrame(position_data, columns=["x", "y", "z"])

fig = go.Figure()
# Scatter plot: x vs y, colored by z
# fig = px.scatter_3d(
#     df, x="x", y="y", z ="z",
#     title="3D Scatter Plot of Position Data",
#     labels={"x": "X Position", "y": "Y Position", "color": "Z Position"},
    # opacity=0.7
# )
fig.update_layout(
    title=f"Difference Trajectory, Q = {Q1:.1e} C and Q2= {Q2:.1e} C<br>"
          f"Coil Offsets = &plusmn;{c:.0f} m, I = {I:.0f} kA, R = {R:.2f} m,<br>"
          f"Washer Offsets = &plusmn;{c:.0f} m, 2a = {a:.2f} m, 2b = {b:.2f} m",
    scene=dict(aspectmode="cube")
)

fig.show()

# source_dir = "/Users/fwessel/Documents/Boris_Usr/Outputs/Custom/100000.0/Magpy/washer_potential/comparisons/"
source_dir = "C:/Users/dylan/OneDrive/Documents/Boris_Usr/Outputs/Custom/100000.0/Magpy/washer_potential/"

file1 = "ns-90000_dt-2e-09_10/data.hdf5"
file1_path = source_dir + file1
print('file1 path =', file1_path)
print("is this correct? If not, please input new value")
file1_path = input('Enter your input:')
print("New Value=", file1_path)

file2 = "ns-90000_dt-2e-09_11/data.hdf5"
file2_path = source_dir + file2
print('file2 path =', file2_path)
print("is this correct? If not, please input new value")
file2_path = input('Enter your input:')
print("New Value=", file2_path)

file_path = "data_new2.hdf5"
with h5py.File(file1_path,file2_path, "r") as f1, f2:
    dset1 = f1["src/position"][:]
    dset2 = f2["src/position"][:]

    ig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "scatter3d"}, {"type": "scatter3d"}]],
        subplot_titles=("Trajectory: data_zero.hdf5", "Trajectory: data_1e-9_2.hdf5")
    )

    # 1. Trajectory
    fig.add_trace(go.Scatter3d(
        x=df1["px"], y=df1["py"], z=df1["pz"],
        mode="lines",
        line=dict(color="blue", width=3),
        name="Trajectory",
        showlegend=True
    ),
        row=1, col=1
    )

    # --- Right plot: Trajectory from file 2 ---
    fig.add_trace(
        go.Scatter3d(
            x=df_diff["px"], y=df_diff["py"], z=df_diff["pz"],
            mode="lines",
            line=dict(color="red", width=3),
            name="Differential Trajectory"
        ),
        row=1, col=2
    )
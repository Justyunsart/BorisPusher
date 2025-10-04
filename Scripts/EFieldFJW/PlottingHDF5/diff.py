'''This script plots the particle trajectory for two Boris Push simulations. It is useful to visualize each
 trajectory and the magnitude of the difference between each trajectory, point by point. When the script is run
it opens a shell window, twice, sequentially, prompting the user to identify the HDF5 data files. The output is
plotted using Plotly, which allows for 3D control of the viewing angle and zoom aspect. The plot header includes
most of the information used for the simulation variables and soon, all of that data will be automatically grabbed
from the folder where the HDF5 data file is stored.
'''
import h5py
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import tkinter as tk
from tkinter import filedialog
from diffVector import plot_difference_vectors_lines

''' This is a script to plot differences in BorisPlots.py particle trajectories, using the HDF5 data as inputs'''

# --- Cube and Washer Parameters ---
I = 100 # kA
R = 1.7/2   # coil radius
c = 1.1  # cube half width
a = 0.25/2  # radius inner  of washer
b = 0.75/2  # radius outer of washer
Q1 = 0e-0 # coulombs
# Q2 = 0e-0 # coulombs
Q2 = 1e-9 # coulombs

def load_positions(filepath):
    """Load src/position dataset into a DataFrame with x,y,z columns."""
    with h5py.File(filepath, "r") as f:
        dset = f["src/position"][:20000]
    # Handle structured or plain array
    if dset.dtype.names is not None:
        return pd.DataFrame({name: dset[name] for name in dset.dtype.names})
    else:
        return pd.DataFrame(dset, columns=["px", "py", "pz"])

# --- File selection with verification ---
def select_files():
    while True:
        root = tk.Tk() # Open root window
        root.withdraw()  # Hide the root window

        print("Select the first HDF5 file:")
        file_path1 = filedialog.askopenfilename(title="Select first HDF5 file")
        print("Select the second HDF5 file:")
        file_path2 = filedialog.askopenfilename(title="Select second HDF5 file")
        print("\nYou selected:")
        print(" File 1:", file_path1)
        print(" File 2:", file_path2)
        choice = input("\nConfirm files? [y]es / [r]eselect / [e]xit: ").strip().lower()

        if choice == "y":
            return file_path1, file_path2
        elif choice == "r":
            print("\nReselecting files...\n")
            continue
        elif choice == "e":
            print("Exiting program.")
            exit(0)
        else:
            print("Invalid choice, please try again.")

# --- Load the trajectory data files---
file_path1, file_path2 = select_files()
df1 = load_positions(file_path1)
df2 = load_positions(file_path2)

print(file_path1)
print(file_path2)

# --- Ensure equal length of the files ---
n = min(len(df1), len(df2))
df1 = df1.iloc[:n].reset_index(drop=True)
df2 = df2.iloc[:n].reset_index(drop=True)

# --- Difference trajectory ---
df_diff = df1 - df2

# --- Circle generation ---
def make_circle(R, n_points=200):
    theta = np.linspace(0, 2 * np.pi, n_points)
    X = R * np.cos(theta)
    Y = R * np.sin(theta)
    Z = np.zeros_like(X)
    return X, Y, Z



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
# Add a circle for the starting points
fig.add_trace(go.Scatter3d(
    x=[df1.loc[0, "px"]],
    y=[df1.loc[0, "py"]],
    z=[df1.loc[0, "pz"]],
    mode="markers",
    marker=dict(size=8, color="black", symbol="circle"),
    name="Start Point",
    showlegend=True
))
# 1a. Plot the Trajectory for df1 (blue)
fig.add_trace(go.Scatter3d(
    x=df1["px"], y=df1["py"], z=df1["pz"],
    mode="lines",
    line=dict(color="blue", width=4),
    name="Trajectory Q1",
    showlegend=True
))
# 1b. Plot the Trajectory for df2 (green)
fig.add_trace(go.Scatter3d(
    x=df2["px"], y=df2["py"], z=df2["pz"],
    mode="lines",
    line=dict(color="green", width=3),
    name="Trajectory Q2",
    showlegend=True
))
# 1c. Plot the diff Trajectory (red)
fig.add_trace(go.Scatter3d(
    x=df_diff["px"], y=df_diff["py"], z=df_diff["pz"],
    mode="lines",
    line=dict(color="red", width=4),
    name="Diff. Trajectory, Q1-Q2",
    showlegend=True
))

# 2. Add the Wireframe Cube
cube_range = [-c, c]
for x in cube_range:
    for y in cube_range:
        fig.add_trace(go.Scatter3d(x=[x,x], y=[y,y], z=cube_range,
                                   mode="lines", showlegend = False,
                                   line=dict(color="black")))
for x in cube_range:
    for z in cube_range:
        fig.add_trace(go.Scatter3d(x=[x,x], y=cube_range, z=[z,z],
                                   mode="lines", showlegend = False,
                                   line=dict(color="black")))
for y in cube_range:
    for z in cube_range:
        fig.add_trace(go.Scatter3d(x=cube_range, y=[y,y], z=[z,z],
                                   mode="lines", showlegend = False,
                                   line=dict(color="black")))

# 3. Add Washers on cube faces
X0, Y0, Z0 = make_washer(a, b)
for orient in ['x+','x-','y+','y-','z+','z-']:
    X, Y, Z = transform_coords(X0, Y0, Z0, orient, c)
    fig.add_surface(x=X, y=Y, z=Z, colorscale="Viridis", showscale=False, opacity=0.6, showlegend = False)


# 4. Add Circles on cube faces
X0, Y0, Z0 = make_circle(R)
for orient in ['x+','x-','y+','y-','z+','z-']:
    X, Y, Z = transform_coords(X0, Y0, Z0, orient, c)
    fig.add_trace(go.Scatter3d(
        x=X, y=Y, z=Z,
        mode="lines",
        line=dict(color="green", width=4),
        name=f"Circle {orient}",
        showlegend=False
    ))

# Final layout
fig.update_layout(
    title=f"Trajectory Comparison: Q1 = {Q1:.1e} C and Q2= {Q2:.1e} C<br>"
          f"Coil Offsets = &plusmn;{c:.1f} m, I = {I:.0f} kA, 2R = {2*R:.2f} m,<br>"
          f"Washer Offsets = &plusmn;{c:.1f} m, 2a = {2*a:.2f} m, 2b = {2*b:.2f} m",
    scene=dict(aspectmode="cube")
)


# --- Call it ---
plot_difference_vectors_lines(df1, df2, step=20, colorscale="Rainbow")

fig.show()


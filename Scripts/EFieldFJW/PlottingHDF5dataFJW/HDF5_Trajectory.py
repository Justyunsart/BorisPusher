import numpy as np
import h5py
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def trajectory():
    file_path = "data.hdf5"
    with h5py.File(file_path, "r") as f:
        dset = f["src/position"][:]
# Case 1: structured dtype (named fields like ('x','y','z'))
    if dset.dtype.names is not None:
        df = pd.DataFrame({name: dset[name] for name in dset.dtype.names})
# Case 2: plain array (N,3)
    elif dset.ndim == 2 and dset.shape[1] == 3:
        df = pd.DataFrame(dset, columns=["px", "py", "pz"])
    else:
        raise ValueError(f"Unexpected dataset shape {dset.shape} and dtype {dset.dtype}")

#     fig.add_trace(
#         go.Scatter3d(df, x="px", y="py", z="pz", mode="markers",)
# )
#     fig = go.Figure()

# 3D scatter plot
    fig = px.scatter_3d(
        df, x="px", y="py", z="pz",
        title="3D Scatter Plot of Position Data",
        opacity=0.7
    )
    return fig
    # fig.show()

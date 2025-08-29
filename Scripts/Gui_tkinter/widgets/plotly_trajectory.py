
"""
atop a stationary view of the whole trajectory situation, add another button that opens a browser
plotly interactive graph with a slider for animation.
"""
import plotly.graph_objects as go
import h5py
import magpylib as magpy
import numpy as np
from pathlib import Path

def graph_trajectory_plotly(hdfpath, collection:magpy.Collection):
    with h5py.File(hdfpath, mode='r') as f:
        df = f['src/position']
        x, y, z = df["px"], df["py"], df["pz"]  # x, y, z coord points at each step

    cut = int(x.shape[0] // 1000) #intervals for animation
    sensArray = np.column_stack((x, y, z))
    sensArrayCut = sensArray[0::cut]
    partSens = magpy.Sensor(pixel=[(0, 0, 0)], style_size=1)
    partSens.position = sensArrayCut

    with magpy.show_context(collection, animation=True, backend='plotly', opacity=0.5):
        magpy.show(partSens, col=1)
        magpy.show(partSens, output='B', col=2, pixel_agg=None)

from Gui_tkinter.funcs.GuiEntryHelpers import File_to_Collection, tryEval
def graph_trajectory_plotly_abstraction_layer(path_var, *args):
    """
    Because the current file's path to read is held in a tkinter var, we need that as an input.
    """
    try:
        hpath = path_var.get()
        c = File_to_Collection(hpath, converters={"Amp": tryEval, "RotationAngle": tryEval, "RotationAxis": tryEval})
        graph_trajectory_plotly(hpath, c)
    except:
        pass


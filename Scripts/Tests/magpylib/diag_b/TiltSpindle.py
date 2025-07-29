#
#
import magpylib as magpy
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
#
#
# Construct two coils from windings
coil1 = magpy.Collection(style_label="coil1")
for z in np.linspace(-0.0005, 0.0005, 3):
    coil1.add(magpy.current.Circle(current=-1, diameter=0.05, position=(0, 0, z)))
coil1.position = (0, 0, -0.015)
#
coil2 = magpy.Collection(style_label="coil2")
for z in np.linspace(-0.0005, 0.0005, 3):
    coil2.add(magpy.current.Circle(current=1, diameter=0.05, position=(0, 0, z)))
coil2.position = (0, 0, 0.015)

# SPINDLECUSP consists of two coils
spindle = coil1 + coil2

# Move the spindle
#spindle.position = np.linspace((0, 0, 0), (0.05, 0.05, 0.05), 15)
spindle.rotate_from_angax(np.linspace(0, 45, 25), "y", start=0)
spindle.rotate_from_angax(np.linspace(0, 45, 25), "z", start=0)

# Move the coils
#coil1.move(np.linspace((0, 0, 0), (0.005, 0, 0), 15))
#coil2.move(np.linspace((0, 0, 0), (-0.005, 0, 0), 15))

# Move the windings
#for coil in [coil1, coil2]:
#    for i, wind in enumerate(coil):
#        wind.move(np.linspace((0, 0, 0), (0, 0, (2 - i) * 0.001), 15))

# Display as animation
fig = go.Figure()
magpy.show(*spindle, animation=True, style_path_show=False, canvas=fig)
fig.add_trace(go.Scatter3d( x=(-0.03,0.03), y=(-0.03,0.03), z=(-0.03,0.03) ))
fig.show()
#how to combine the show of Fig and *spindle together !!!
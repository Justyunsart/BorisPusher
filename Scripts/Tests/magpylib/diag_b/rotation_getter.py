import magpylib as mp
from magpylib.current import Circle
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
from Scripts.Tests.fields.graphing_funcs import GraphB
import plotly.io as pio
pio.renderers.default = "browser"
from MakeCurrent import Circle as cir

@dataclass
class rotation_param():
    degrees: float = 0.0
    axis: str = 'x'

def do_rotation(circle:Circle, rotations:list, show_animation=True, show_final_B=True):
    num_steps = 100
    # perform rotations
    for rotation in rotations:
        # create the linspace for animation if you need to
        if show_animation:
            degrees = np.linspace(0, rotation.degrees, num_steps)
        else:
            degrees = rotation.degrees
        circle.rotate_from_angax(degrees, rotation.axis)

    col = cir(1000, 2, 1.1, 0)
    col.add(circle)

    # show the final B-field
    if show_final_B:
        final_B_fig = plt.figure()
        final_B_ax = final_B_fig.add_subplot(111)

        GraphB(col, final_B_ax, final_B_fig)

    if show_animation:
        mp.show(col, animation=True, backend='plotly')
        plt.show()



if __name__ == '__main__':
    # runtime parameters
    show_animation = False
    show_final_B = True

    # DEFINE CIRCLE
    circle = Circle(position=(0,0,0), diameter=2, current=100)

    # DEFINE ROTATIONS
    rotations = [rotation_param(degrees=90, axis='x'),
                 rotation_param(degrees=90, axis='y'),
                 rotation_param(degrees=90, axis='z'),]

    do_rotation(circle, rotations, show_animation=show_animation, show_final_B=show_final_B)
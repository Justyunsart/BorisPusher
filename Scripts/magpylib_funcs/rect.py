import magpylib as mpl
from magpylib.current import Polyline
import numpy as np

"""
Helper function. From high-level parameters, returns its rect vertices as a 2d array
"""
def get_vertices_from_center(center, width, height):
        # the 2d array has a known shape
    out = np.empty((4, 3), dtype=np.float64)

        # get the horizontal and vertical offsets from the centerpoint
    xoffset = [width / 2, 0, 0]
    yoffset = [0, height / 2, 0]

    out[0] = center + xoffset + yoffset
    out[1] = center - xoffset + yoffset
    out[2] = center - xoffset - yoffset
    out[3] = center + xoffset - yoffset

    return out

"""
Shortcut to create a rectangular coil, consisting of preconfigured polylines.
"""
def create_rect(center_position, width, height, orientation=None):
    out = Polyline()
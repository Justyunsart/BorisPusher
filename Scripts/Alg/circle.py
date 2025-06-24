import numpy as np
import scipy as sp

"""
Helper functions for operations on circles.
"""

def circle_trace(npoints=200, radius=1):
    """
    returns an array of points of shape (npoints, 3)
    which represents the coordinates of a circle with the given radius (default=1)

    npoints is 200 by default.
    """

    # generate theta values
    thetas = np.linspace(0, 2*np.pi, npoints)

    # calculate for the x and y coordinate elements of the circle
    rx = np.cos(thetas) * radius
    ry = np.sin(thetas) * radius
    rz = np.zeros(npoints)

    return np.vstack([rx, ry, rz]).T
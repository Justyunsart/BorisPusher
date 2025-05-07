import matplotlib.pyplot as plt
import numpy as np
from Scripts.calcs.grid import index_cross_sections

"""
Function to plot a b-field streamline of a cross section.

# Parameters
xlab, ylab = strings to label the x and y axes with
ax = a matplotlib subplot. if not provided, it will create one just for demo purposes.

# Notes
> b_grid and grid must be of the same shape!!!! 
"""
def plot_b(b_grid, grid, ax=None,):
    X, Y = grid
    U, V = b_grid
    # create an axis and figure if nothing is provided.
    if ax is None:
        ax = plt.figure().add_subplot()
    
    ax.streamplot(X.T, Y.T, U.T, V.T, density=1, color=np.log(U**2 + V**2))

    return ax

"""
Assumes a pre-populated b_field grid info.
"""
def plot_b_crosses(b_grid, grid, plots):
    planes = ['xz', 'xy', 'yz'] # the order of plane cut plots
    
    for i in range(3):
        # The grids are (n, n, n, 3), and we want to output (2, n, n).
        # First reshape
        _b = np.swapaxes(b_grid, 0, 3)

        b_grid_ind = index_cross_sections(_b, planes[i])
        grid_ind = index_cross_sections(grid, planes[i])

        plot_b(b_grid_ind, grid_ind, plots[i])

        plots[i].set_title(f"{planes[i]} - Plane")

    return True
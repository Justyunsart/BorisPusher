import tkinter as tk

import matplotlib.pyplot as plt
from Scripts.calcs.grid import generate_square_meshgrid_3d
from Scripts.calcs.bfield_plt import plot_b_crosses
import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

"""
Part of the coils tab.
A popup window that contains multiple figures of different cross section streamline plots.
Created on a button press so that the graphing functions are not excessively called.
The window will also close automatically when clicking on anything outside it.


# WIDGET FORMAT FOR GRAPHS
Lowest to highest level:
    Frame -> Canvas -> FigureCanvasTkAgg(plt.figure())
"""
class b_crosses_window():
    def __init__(self, master, c, lim=3, res=100):
        self.c = c
        self.lim = lim
        self.res = res
        
        # create the window where everything sits on
        self.toplevel = tk.Toplevel(master=master)
        self.toplevel.title("B-field Cross Sections")
        self.toplevel.resizable(False, False) # you cannot resize this window.
        self.mainframe = tk.Frame(self.toplevel) # main parent container.
        self.canvas = tk.Canvas(self.mainframe)

        # set up subplots and figure canvas
        self.setup_axes()

        # plot after graphs init
        self.populate_plots()

        # packing
        self.mainframe.pack()
        self.canvas.pack()
        self.FigCanvas.get_tk_widget().pack()

        # event binding
        self.toplevel.bind("<FocusOut>", self.close_window) # close the window when you click off to something else
    
    def close_window(self, event=None):
        self.toplevel.destroy()

    """
    Creates the coordinate and B meshgrids.
    """
    def get_grid_info(self):
        self.grid = generate_square_meshgrid_3d(self.lim, self.res)
        self.b_grid = self.c.getB(np.swapaxes(self.grid,0,3))

    """
    Sets up the figure and axes
    """
    def setup_axes(self):
        # make the figure and subplots
        self.fig = plt.figure()

        ax1 = self.fig.add_subplot(131)
        ax2 = self.fig.add_subplot(132)
        ax3 = self.fig.add_subplot(133)

        self.subplots = [ax1, ax2, ax3] # iterable for all axes.

        # we will use that iterable for plotting all the cross sections. Also for this:
        for ax in self.subplots:
            ax.set_box_aspect(1)

        # make the FigureCanvasTkAgg object that will display the mpl figures.
        self.FigCanvas = FigureCanvasTkAgg(figure=self.fig, master=self.canvas)
        self.toolbar = NavigationToolbar2Tk(canvas=self.FigCanvas, window=self.canvas) # figure toolbar

    """
    After the figure and axes are initialized, we can now run the graphing functions.
    """
    def populate_plots(self):
        self.get_grid_info() # this stores the meshgrid and its b-field.
        plot_b_crosses(self.b_grid, self.grid, self.subplots)
        self.FigCanvas.draw()

"""
Function to initialize the b_crosses_window class.
"""
def open_b_cross_window(master, c, lim=3, res=100, event=None):
    window = b_crosses_window(master, c, lim, res)

if __name__ == "__main__":
    from Scripts.debug.empty_app import create_button_tk
    from Scripts.debug.collection import mirror
    from functools import partial

    # create the app
    root, mainframe, button = create_button_tk()
    c = mirror()

    # configure button to open the tested widget
    button.configure(command=partial(open_b_cross_window, mainframe, c))

    # run mainloop
    root.mainloop()
import matplotlib.pyplot as plt
import numpy as np

"""
Classes related to field visualization options.
Concerned with being an abstraction layer between the individual Solver class instances
and the necessary graphing functionality.
"""
from typing import Type
from EFieldFJW.e_solvers import Solver
from EFieldFJW.e_graphs import Grapher
from Gui_tkinter.widgets.base import ParamWidget

class GraphFactory(ParamWidget):
    """
    Instanced pairings of grapher and solver objects (defined in EFieldFJW.e_graphs and e_solvers)

    To let the collection argument properly update, this class inherits getter funcs from ParamWidget module.
    The collection is collected when the time comes to instantiate.
    """
    def __init__(self, solver:Type[Solver], grapher:Type[Grapher],
                 field:str, params):
        self.solver = solver
        self.grapher = grapher
        self.field = field
        self.params = params

        self.collection_key = f"{field}.collection"

    def make(self):
        return self.grapher(
            self.solver(),
            self.get_nested_field(self.params, self.collection_key)
        )


import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

class FieldDropdownFigure(tk.Frame):
    """
    A frame that controls a dropdown menu, which updates a canvas figure object
    upon option selection.

    Though a class with this functionality does technically exist as PlottingWindow.DropdownFigure,
    I decided to make a more barebones, abstract class for it (since that class was not written with the expectation
    of being made for anything outside the plotting tab).

    Compared to that class in PlottingWindow, this one does not explicitly control graph graphing functions' calls
    """
    def __init__(self, master, option_dict:dict):
        tk.Frame.__init__(self, master)
        self.master = master
        self.option_dict = option_dict
        self.options = list(option_dict.keys())
        self.fig = None
        self.plot = None
        self.cb = None
        self.mappable = None

        # CREATE ORGANIZATIONAL FRAMES #
        ################################
        # A 'top row' frame will house the dropdown + confirm button
        # The rest of the widgets will be below this top frame.
        top_frame = tk.Frame(self)

        # CREATE DROPDOWN WIDGET #
        ##########################
        self.selected_option = tk.StringVar() #tracker for currently selected option
        self.selected_option.set(self.options[0])
        self.dropdown = tk.OptionMenu(top_frame, self.selected_option, *self.options)

        # CREATE THE CONFIRM BUTTON #
        #############################
        self.button = tk.Button(top_frame, text="Graph", width=8)

        # CREATE FIGURE CANVAS WIDGET #
        ###############################
        # first, we need to create the figure and axis.
        self.init_fig() #Create figure, plot
        # it can then be placed in a tk.Canvas obj.
        self.canvas = tk.Canvas(self)
        self.canvas_widget = FigureCanvasTkAgg(self.fig, self.canvas)
        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, master)

        # PACKING #
        ###########
        top_frame.pack(side="top", fill="x")
        self.dropdown.pack(side='left', fill='x', expand=True)
        self.button.pack(side='left')
        self.canvas.pack(side='top', fill='both', expand=True)
        self.canvas_widget.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.toolbar.pack(side='bottom', fill='x', expand=True)

    def init_fig(self):
        """
        Instantiates a figure and subplot according to current settings.
        """
        self.fig = plt.figure()
        self.plot = self.fig.add_subplot(1,1,1)
        self.fig.tight_layout()

    def reset_graph(self):
        """
        Clear everything to make room for the next graph to be displayed
        """
        self.plot.cla()
        self.remove_colorbar()

    def remove_colorbar(self):
        if self.cb is not None and getattr(self.cb, 'ax', None) is not None:
            #print(self.cb)
            self.cb.ax.remove()
        self.cb = None

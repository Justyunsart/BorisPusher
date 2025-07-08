"""
Will define the widget that is created in the nested nested notebook tab.

GOAL:
Constructor for a preset configuration of a nested notebook tab.
Provide the name of the notebook tab, alongside a class (child of a tk.Frame) to display.
Save automatically to the state dictionary
"""
import tkinter as tk
from tkinter import ttk
from system.temp_manager import TEMPMANAGER_MANAGER
from system.temp_file_names import param_keys, m1f1

class Field_Notebook(ttk.Notebook):
    """
    Parameters:
        master: the parent widget that owns this notebook
        tab_names, tab_widgets: lists that contain the respective notebook tab names, alongside their displayed widgets.
    """
    def __init__(self, master, tab_names:list, tab_widgets:list, **kwargs):
        def _check_notebook_inputs() -> None:
            """
            Function that is just a container for all the assert statement for this class
            """
            assert len(self.tab_names) == len(self.tab_widgets), f"{len(self.tab_names)} != {len(self.tab_widgets)}"

        # PRE-CREATION
        # init the super
        super().__init__(master, **kwargs)
        # define instance attributes
        self.tab_names = tab_names
        self.tab_widgets = tab_widgets
        # check the legality of inputs
        _check_notebook_inputs()

        # CONFIGURE STRUCTURE
        def _add_notebook_tabs() -> None:
            pass

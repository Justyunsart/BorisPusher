"""
Will contain the field method options for the B and E fields, and their associated tables/widgets.
"""
import tkinter as tk
from tkinter import ttk

"""
The main container widget that will go in the tk.notebook.
Make it have the least amount of input parameters as possible!
"""
class CoilWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
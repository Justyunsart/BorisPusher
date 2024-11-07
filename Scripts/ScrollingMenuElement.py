import tkinter as tk
"""
Given an input of a nested dictionary structure (currently max. of 1 nest),
and the desired font settings for these headings,

Create a class of tkinter widgets that organizes desired settings in the scrollable frame format.
"""

class Heading_n_Separator(tk.Frame):
    """
    Displays the heading name, and a separator line for visual clarity

    
    PARAMS:
    
    name:str
         - The text to be displayed as the heading
    nesting:0|1
         - Level of nesting the widget is at.
         - The more nested this is, the smaller the font size gets, typically.
         - Currently only goes up to 1 nest, hence the value is either 0 or 1.
    """
    def __init__(self, master, name:str, nesting:0|1):
        pass

class Setting(tk.Frame):
    def __init__(self, master, name:str, type=float):
        pass
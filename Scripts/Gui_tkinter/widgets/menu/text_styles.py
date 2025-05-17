
"""
Shortcuts so I don't have to continually import the color palette and fiddle with tk.Label parameters.
I just want to make each associated font type its own widget essentially.
"""

from settings.palettes import Font_n_Color
import tkinter as tk

class GUI_Label(tk.Label):
    def __init__(self, master, font:Font_n_Color, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(font=font.font, fg=font.color)

import tkinter as tk
from ScrollableFrame import ScrollableFrame

"""
Window that pops up when the corresponding
toolbar button is pressed.

Reads and edits things I deem worthy of being user editable.
"""

# Defaults to use in case of errors, or if unedited.
default_text_settings = {"size" : {"normal" : 18, "heading 1" : 20},
                 "font" : "arial"}

#############################
# TOPLEVEL CLASS DEFINITION #
#############################
class Pref_Window(tk.Toplevel):
    def __init__(self, master, **kwargs):

        # Initialize the toplevel window.
        self.master = master
        super().__init__(master, **kwargs)

        # Create the scrollable element.
        self.scrollable = ScrollableFrame(self)


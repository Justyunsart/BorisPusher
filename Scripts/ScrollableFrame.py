import tkinter as tk

class ScrollableFrame(tk.Canvas):
    """
    With a predefined desired minimum width and height,
    puts all widgets, frames in a scrollable format.

    PARAMETERS:
    master: tk.Frame
         - the container where this element will reside
    """
    def __init__(self, master:tk.Frame, **kwargs):
        # master is expected to be a tk.Frame object.
        self.master = master
        self.scrollbar_v = tk.Scrollbar(master) # scrollbar has to be parented by the frame
        
        # Initialize the canvas with the scrollbar set as the scroll command
        super().__init__(master, yscrollcommand=self.scrollbar_v.set, **kwargs)

        self.scrollbar_v.config(command=self.yview)
        self.scrollbar_v.pack(side="left", fill="y")

        # This is the frame that is contained within the scrollable canvas.
        self.frame = tk.Frame(self)            

        # Packing
        self.pack(side="left", fill="both", expand="True")

        self.create_window(0,0, window=self.frame, anchor="nw")

    def RegisterScrollArea(self):
        """
        Run this after adding all relevant widgets.
        Defines the space they take up as the scrolling region.
        """
        self.config(scrollregion=self.bbox("all"))
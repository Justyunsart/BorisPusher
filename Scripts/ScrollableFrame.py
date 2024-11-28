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

        # This is the frame that is contained within the scrollable canvas.
        self.frame = tk.Frame(self)          
        
        # Bind self to re-register the scroll area upon window dimension change
        self.bind('<Configure>', self._on_Configure)

    def _on_Configure(self, event):
        """
        Intended to run whenever the root window's dimensions change.
            - resize the frame
            - update the scroll area.
        """
        # Get updated window width
        w = event.width

        # Adjust the canvas element(self) to the updated width, to match
        self.itemconfig(self.window, width = w)

        # Re-register the scroll dimensions of the canvas
        self.RegisterScrollArea()

    def RegisterScrollArea(self):
        """
        Run this after adding all relevant widgets.
        Defines the space they take up as the scrolling region.
        """
        #print("resize detected")
        self.config(scrollregion=self.bbox("all"))

    def _InternalPack(self):
        """
        Put here so we can explicitly control packing order from a high level.
        """
        self.scrollbar_v.pack(side="left", fill="y")
        self.window = self.create_window(0,0, window=self.frame, anchor="nw")
        self.pack(fill="both", expand=True, side="top")
        #self.frame.pack(fill="both", expand=True, side="top")
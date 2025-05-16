import tkinter as tk
from Scripts.Gui_tkinter.widgets.ScrollableFrame import ScrollableFrame

"""
What gets spawned when the menubar's settings option is pressed. Basically is a popup window
that lets you tinker with parameters used in config.ini.

as of 5/14, this is just the dir location of the inputs folder.
"""

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Settings")
        #self.geometry("400x300")

        ##############################################
            # High level frames
        frame0 = tk.Frame(self) # bottommost thing with persistent buttons
        frame1 = tk.Frame(self) # main content

            # Main content (inside frame1)
        mainframe = ScrollableFrame(frame1)

            # Configuring
            # Make the bottom row at a constant pixel height
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0, minsize=30, pad=5)
        self.columnconfigure(0, weight=1)

            # Packing
        frame1.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        frame0.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)

        mainframe.frame.grid(row=0, column=0, sticky=tk.NSEW)

        ##############################################
            # Widgets on the bottom row of the toplevel; persistent
        self.button_ok = tk.Button(frame0, text="Ok", width=8, height=2)
        self.button_exit = tk.Button(frame0, text="Exit", width=8, height=2)

            # Packing
        self.button_ok.pack(side=tk.RIGHT, padx=5)
        self.button_exit.pack(side=tk.RIGHT, padx=5)


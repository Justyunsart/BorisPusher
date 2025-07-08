from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Gui_tkinter.widgets.Bob_e_Circle_Config import Bob_e_Circle_Config
from settings.configs.funcs.config_reader import runtime_configs
from definitions import NAME_BOB_E_CHARGES
import tkinter as tk
import os



"""
There are currently two expected values for the field configuration notebook's individual tab widgets.

For the Zero field, the widget is going to be blank basically
For anything requiring ring configuration (everything else), there's going to be input tables and graphs and stuff.
"""

class ZeroTableTab(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)

        # debug label
        label = tk.Label(self, text="Zero Table Tab").grid(row=0, column=0)

        # pack self
        self.grid(row=0, column=0, sticky=tk.NSEW)


class RingTableTab(tk.Frame):
    """
    A frame containing:
        - a current table
        - a preview graph
    MUST also communicate with the manager
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args)
        self.root = parent

        self.frame1 = tk.Frame(self)
        self.frame1.grid(row=2, column=0)
        self.frame2 = tk.Frame(self)
        self.frame2.grid(row=3, column=0)

        self.widget_frames = [self.frame1, self.frame2]

        # self.q = LabeledEntry(self.frame1, .1, row=1, col=0, title="q: ", width=10)
        self.res = LabeledEntry(self.frame1, 100, row=1, col=1, title="res: ", width=10)

        # Coil Config
        self.table = Bob_e_Circle_Config(self.frame2,
                                         dir=os.path.join(runtime_configs['Paths']['inputs'], NAME_BOB_E_CHARGES), **kwargs)
        self.widgets = [self.table, self.res]
        self.table.grid(row=0)

        # self.q.value.trace_add("write", self.trigger_listener)
        #self.res.value.trace_add("write", self.trigger_listener)

        # pack self
        self.grid(row=0, column=0, sticky=tk.NSEW)
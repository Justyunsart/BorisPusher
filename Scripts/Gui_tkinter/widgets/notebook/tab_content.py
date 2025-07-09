from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Gui_tkinter.widgets.Bob_e_Circle_Config import Bob_e_Circle_Config
from settings.configs.funcs.config_reader import runtime_configs
from definitions import NAME_BOB_E_CHARGES
from system.temp_file_names import param_keys, m1f1
import tkinter as tk
import os
from PIL import ImageTk, Image
import definitions

from system.temp_manager import update_temp, TEMPMANAGER_MANAGER
"""
There are currently two expected values for the field configuration notebook's individual tab widgets.

For the Zero field, the widget is going to be blank basically
For anything requiring ring configuration (everything else), there's going to be input tables and graphs and stuff.
"""

class ZeroTableTab(tk.Frame):
    img_path = os.path.normpath(os.path.join(definitions.DIR_ROOT, f"Scripts/system/imgs/zero_field.png"))
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)

        # display indicator image
        self.im_label = tk.Label(self)
        self.im = ImageTk.PhotoImage(Image.open(self.img_path))
        self.im_label.config(image=self.im)

        # pack self
        self.im_label.grid(row=0, column=0)
        self.grid(row=0, column=0, sticky=tk.NSEW)



class RingTableTab(tk.Frame):
    """
    A frame containing:
        - a current table
        - a preview graph
    MUST also communicate with the manager
    """
    def __init__(self, parent, dir_name, *args, **kwargs):
        self.listeners = []
        tk.Frame.__init__(self, parent, *args)
        self.add_listener(parent)
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
                                         dir=os.path.join(runtime_configs['Paths']['inputs'], dir_name), **kwargs)
        self.widgets = [self.table, self.res]
        self.table.grid(row=0)

        # self.q.value.trace_add("write", self.trigger_listener)
        self.res.value.trace_add("write", self.trigger_listener)

        # pack self
        self.grid(row=0, column=0, sticky=tk.NSEW)

    # Some observer methods to handle basic event handling
    def add_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)

    def trigger_listener(self, *args):
        for listener in self.listeners:
            listener.update(
                [param_keys.field_methods.name, 'e', param_keys.params.name, 'res'],
                self.res.value.get())

class DiskTab(RingTableTab):
    def __init__(self, parent, dir_name, *args, **kwargs):
        RingTableTab.__init__(self, parent, dir_name, *args, **kwargs)

        # update the instanced version of the entryvalidatecallback to the modified one
        self._modify_entryvalidate_callback()

    def _modify_entryvalidate_callback(self):
        print("I am modifying entry validate callback")
        print("Monkey-patching EntryValidateCallback...")
        print("Wrapped func:", self.table.entry_table.GraphCoils)
        original_method = self.table.entry_table.GraphCoils

        def wrapped_func(*args, **kwargs):
            print(f"HEY HEY HEY")
            original_method(*args, **kwargs)
            data = self.table.entry_table.GetData()
            print("Data fetched:", data)
            innies = data['Inner_r']
            update_temp(TEMPMANAGER_MANAGER.files[m1f1], {"field_methods":{'e':{"params":{"Inner_r" : innies}}}})

        self.table.entry_table.GraphCoils = wrapped_func
        print("EntryValidateCallback at runtime:", self.table.entry_table.GraphCoils)

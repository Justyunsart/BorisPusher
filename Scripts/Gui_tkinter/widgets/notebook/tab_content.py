from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Gui_tkinter.widgets.Bob_e_Circle_Config import Bob_e_Circle_Config
from settings.configs.funcs.config_reader import runtime_configs
from definitions import NAME_BOB_E_CHARGES
from system.temp_file_names import param_keys, m1f1
import tkinter as tk
import os
from PIL import ImageTk, Image
import definitions
from functools import partial

from system.temp_manager import update_temp, TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
"""
There are currently two expected values for the field configuration notebook's individual tab widgets.

For the Zero field, the widget is going to be blank basically
For anything requiring ring configuration (everything else), there's going to be input tables and graphs and stuff.
"""

class ZeroTableTab(tk.Frame):
    img_path = os.path.normpath(os.path.join(definitions.DIR_ROOT, f"Scripts/system/imgs/zero_field.png"))
    def __init__(self, parent, dir_name="", field="", *args, **kwargs):
        tk.Frame.__init__(self, parent)
        # hold diagnostic
        self.dir_name = dir_name

        # display indicator image
        self.im_label = tk.Label(self)
        self.im = ImageTk.PhotoImage(Image.open(self.img_path))
        self.im_label.config(image=self.im)

        # pack self
        self.im_label.grid(row=0, column=0)
        self.grid(row=0, column=0, sticky=tk.NSEW)

    def onActive(self, tab_key, collection_key, text, is_init=False):
        def set_nested_value(d, keys, value):
            """Set a value in a nested dictionary given a list of keys."""
            for key in keys[:-1]:
                d = d.setdefault(key, {})  # ensures intermediate dicts exist
            d[keys[-1]] = value
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])

        # set the collection value to 'None'
        set_nested_value(d, list(collection_key), "None") # doesn't seem to work but doesnt matter lol

        write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)



class RingTableTab(tk.Frame):
    """
    A frame containing:
        - a current table
        - a preview graph
    MUST also communicate with the manager
    """
    def __init__(self, parent, dir_name, field, *args, **kwargs):
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
                                         dir=os.path.join(runtime_configs['Paths']['inputs'], dir_name), dir_name=dir_name, **kwargs)
        self.widgets = [self.table, self.res]
        self.table.grid(row=0)

        # checkbox for gridding
        self.gridding_var = tk.IntVar()
        self.gridding = tk.Checkbutton(self.frame2, text="precompute grid", variable=self.gridding_var)
        self.gridding.grid(row=1, column=0)

        gridding_func = partial(self.trigger_listener, [param_keys.field_methods.name, field, param_keys.params.name, 'gridding'],
                                self.gridding_var)
        self.gridding_var.trace_add("write", gridding_func)

        # self.q.value.trace_add("write", self.trigger_listener)
        listener_func = partial(self.trigger_listener, [param_keys.field_methods.name, field, param_keys.params.name, 'res'],
                                self.res)
        self.res.value.trace_add("write", listener_func)

        # init. values on start
        gridding_func()
        listener_func()

        # pack self
        self.grid(row=0, column=0, sticky=tk.NSEW)

    # BASIC EVENT HANDLING: for the param 'res', which is assumed

    # to only be used for E field methods.
    # Some observer methods to handle basic event handling
    def add_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)

    def trigger_listener(self, lst, val, *args):
        for listener in self.listeners:
            listener.update(
                lst,
                val.get())

    def onActive(self, tab_key, collection_key, text, is_init=False):
        #print(f"RingTableTab.onActive running")
        if is_init:
            self.table.entry_table.read_last_used()
            return

        # when the tab becomes active, update the graph (which updates the runtime dict)
        self.table.entry_table.GraphCoils()

class DiskTab(RingTableTab):
    """
    Extension of the RingTableTab class, with the assumption that this will be used with
    the disk_e method.
    """
    def __init__(self, parent, dir_name, *args, **kwargs):
        RingTableTab.__init__(self, parent, dir_name, *args, **kwargs)

        # update the instanced version of the entryvalidatecallback to the modified one
        self._modify_entryvalidate_callback()

    def _modify_entryvalidate_callback(self):
        original_method = self.table.entry_table.GraphCoils

        def wrapped_func(*args, **kwargs):
            def set_nested_value(d, keys, value):
                """Set a value in a nested dictionary given a list of keys."""
                for key in keys[:-1]:
                    d = d.setdefault(key, {})  # ensures intermediate dicts exist
                d[keys[-1]] = value

            original_method(*args, **kwargs)
            # sample row for data: {'PosX': '1.1', 'PosY': '0.0', 'PosZ': '0.0', 'Q': '1000.0', 'Diameter': '1.0', 'Rotations': {'Angles': [90], 'Axes': ['y']}, 'Inner_r': '1'}
            # data is a list of these.
            data = self.table.entry_table.GetEntries()
            #print("Data fetched:", data)
            innies = [x['Inner_r'] for x in data]

            # update the runtime dict
            d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
            set_nested_value(d, ['field_methods', 'e', 'params', 'Inner_r'], innies)
            write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

        self.table.entry_table.GraphCoils = wrapped_func
        # also run the function, so that this wrapped logic is applied after being set
        self.table.entry_table.GraphCoils()

    def onActive(self, tab_key, collection_key, text, is_init=False):
        if is_init:
            self.table.entry_table.read_last_used()
            return
        def set_nested_value(d, keys, value):
            """Set a value in a nested dictionary given a list of keys."""
            for key in keys[:-1]:
                d = d.setdefault(key, {})  # ensures intermediate dicts exist
            d[keys[-1]] = value

        # when the tab becomes active, update the graph (which updates the runtime dict)
        self.table.entry_table.GraphCoils()


        # handle method-specific params
        match str(text):
            case 'disk_e':
                # if the selected e method is not 'disk_e', then you can set the key Inner_r's value to None
                d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
                set_nested_value(d, ['field_methods', 'e', 'params', 'Inner_r'], None)
                write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

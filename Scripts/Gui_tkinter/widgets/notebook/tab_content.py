from bokeh.layouts import column
from tables.utilsextension import get_nested_field

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

#from system.temp_manager import update_temp, TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.state_dict_main import AppConfig
from Gui_tkinter.widgets.base import ParamWidget
"""
There are currently two expected values for the field configuration notebook's individual tab widgets.

For the Zero field, the widget is going to be blank basically
For anything requiring ring configuration (everything else), there's going to be input tables and graphs and stuff.
"""

class ZeroTableTab(tk.Frame, ParamWidget):
    img_path = os.path.normpath(os.path.join(definitions.DIR_ROOT, f"Scripts/system/imgs/zero_field.png"))
    def __init__(self, parent, dir_name="", field="", params=None, *args, **kwargs):
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

        self.field = field
        self.params = params

    def set_table_dropdown(self):
        """
        only put here so that it can work with RingTableTab's dynamic function use.
        """
        pass

    def onActive(self, tab_key, collection_key, text=None, is_init=False):
        # update the method attribute of the FieldConfig dataclass
        if not is_init:
            #print(f"Zero's active function is runnng")
            method_path = f"{self.field}.method"
            self.set_nested_field(self.params, method_path, text)
            self.set_nested_field(self.params, f"path.{self.field}", None)



class RingTableTab(tk.Frame, ParamWidget):
    """
    A frame containing:
        - a current table
        - a preview graph
    MUST also communicate with the manager
    """
    def __init__(self, parent, dir_name, field, params, param_class, *args, **kwargs):
        self.listeners = []
        tk.Frame.__init__(self, parent, *args)
        self.params = params
        self.params_field = self.get_nested_field(self.params, f"{field}")
        self.param_class = param_class
        self.add_listener(parent)
        self.root = parent
        self.field = field

        self.frame1 = tk.Frame(self)
        self.frame1.grid(row=2, column=0)
        self.frame2 = tk.Frame(self)
        self.frame2.grid(row=3, column=0)

        self.widget_frames = [self.frame1, self.frame2]

        # self.q = LabeledEntry(self.frame1, .1, row=1, col=0, title="q: ", width=10)
        self.res = LabeledEntry(self.frame1, 100, row=1, col=1, title="res: ", width=10)

        # Coil Config
        self.table = Bob_e_Circle_Config(self.frame2,
                                         dir=os.path.join(runtime_configs['Paths']['inputs'], dir_name), dir_name=dir_name,
                                         params=params, **kwargs)
        self.widgets = [self.table, self.res]
        self.table.grid(row=0)

        # checkbox for gridding
        self.gridding_var = tk.IntVar()
        self.gridding = tk.Checkbutton(self.frame2, text="precompute grid", variable=self.gridding_var)
        self.gridding.grid(row=1, column=0)

        # checkbox for logging
        self.logging_var = tk.IntVar()
        self.logging = tk.Checkbutton(self.frame2, text="log?", variable=self.logging_var)
        self.logging.grid(row=1, column=1)

        # ADD CALLBACKS TO UPDATE PARAMS WHEN THINGS ARE CHANGED.
        # trigger_listener is the function call to lock in changes
        logging_func = partial(self.trigger_listener, f"{field}.logging",
                               self.logging_var)
        self.logging_var.trace_add("write", logging_func)

        gridding_func = partial(self.trigger_listener, f'{field}.gridding',
                                self.gridding_var)
        self.gridding_var.trace_add("write", gridding_func)

        # self.q.value.trace_add("write", self.trigger_listener)
        listener_func = partial(self.trigger_listener, f"{self.field}.res",
                                self.res)
        self.res.value.trace_add("write", listener_func)

        # init. values on start
        gridding_func()
        listener_func()

        # pack self
        self.grid(row=0, column=0, sticky=tk.NSEW)

    def set_table_dropdown(self):
        """
        Expected to run when selecting the last used tab on system initialization.
        If there is a last-used filename stored, and that file exists still,
        have the entry table load that file.
        """
        self.table.entry_table.read_last_used()


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

    def onActive(self, tab_key, collection_key, text=None, is_init=False):
        #print(f"RingTableTab.onActive running")
        if is_init:
            #self.table.entry_table.read_last_used()
            return

        self.table.entry_table.Read_Data()
        # update the configs dataclass with the associated FieldConfig dataclass or subclass
        setattr(self.params, self.field, self.param_class())

        # update the method attribute of the FieldConfig dataclass
        method_path = f"{self.field}.method"
        self.set_nested_field(self.params, method_path, text)

        # when the tab becomes active, update the graph (which updates the runtime dict)
        self.table.entry_table.GraphCoils()
        self.table.entry_table.update_params()

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

            original_method(*args, **kwargs)
            # sample row for data: {'PosX': '1.1', 'PosY': '0.0', 'PosZ': '0.0', 'Q': '1000.0', 'Diameter': '1.0', 'Rotations': {'Angles': [90], 'Axes': ['y']}, 'Inner_r': '1'}
            # data is a list of these.
            data = self.table.entry_table.GetEntries()
            #print("Data fetched:", data)
            innies = [x['Inner_r'] for x in data]

            # update the runtime dict
            self.set_nested_field(self.params, f"{self.field}.inner_r", innies)

        self.table.entry_table.GraphCoils = wrapped_func
        # also run the function, so that this wrapped logic is applied after being set
        self.table.entry_table.GraphCoils()

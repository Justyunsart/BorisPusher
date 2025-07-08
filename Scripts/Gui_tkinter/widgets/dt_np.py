import tkinter as tk
from tkinter import ttk
import numpy as np
from bokeh.layouts import column

from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Gui_tkinter.widgets.BorisGuiClasses import _Try_Float

from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp, update_temp
from system.temp_file_names import manager_1, m1f1, param_keys
from functools import partial
from events.funcs import before_simulation_bob_dt

"""
Associated params for the bob timestep scaling.
    > reference proportion (0: origin, 1: circle's center): Scale from 0 to 1. Determines where on the line to place the ref. particle
    > dynamic range (float): factor for how low/high to look for dtp
"""
class bob_dt_widget(tk.Frame):
    def __init__(self, master, borderwidth=2, relief=tk.SUNKEN):
            # system default values to init with.
        self.defs = {'prop' : "0.5",
                     'dyn_rng' : "10"}

        super().__init__(master)
            # information-holding widgets
                # titles
        self._ref_p = tk.Label(self, text="Reference Proportion: ", justify='left')
        self._dyn_r = tk.Label(self, text="Dynamic Range: ", justify='left')
                
                # entries (var, widget, and event binding)
        self.var_ref_p = tk.DoubleVar(value=self.defs['prop'])
        self.var_dyn_r = tk.DoubleVar(value=self.defs['dyn_rng'])
        self.ref_p = tk.Entry(self, textvariable=self.var_ref_p, justify='center')
        self.dyn_r = tk.Entry(self, textvariable=self.var_dyn_r, justify='center')
        self.ref_p.bind("<KeyRelease>", partial(self.widget_update_tempfile, self.ref_p))
        self.dyn_r.bind("<KeyRelease>", partial(self.widget_update_tempfile, self.dyn_r))

                # PACKING
        self._ref_p.grid(row=0, column=0, sticky='w')
        self.ref_p.grid(row=0, column=1, sticky='e')
        self._dyn_r.grid(row=1, column=0, sticky='w')
        self.dyn_r.grid(row=1, column=1, sticky='e')
    
            # meta info
                # container for state handling (toggle editability)
        self.entries = [self.ref_p, self.dyn_r]
                # mapping to be used in update function
        self.temp_key_map = {self.ref_p : param_keys.dt_bob_prop.name,
                             self.dyn_r : param_keys.dt_bob_dyn_rng.name}

        self.widget_update_tempfile(self.ref_p)
        self.widget_update_tempfile(self.dyn_r)
    
    """
    Expected that check_state contains the value of the parent checkbox widget.
    Changes the editability of self.entries to match this value.
    """
    def toggle_editability(self, val, *args):
        # helper function to shortcut looping through all the associated entries and setting state config.
        def _set_entry_editability(state:str):
            assert state in ('disabled', 'normal')
            for entry in self.entries:
                entry.config(state=state)

        match val.get():
            case 0:
                _set_entry_editability('disabled')
            case 1:
                _set_entry_editability('normal')
    
    """
    Update function for the tempfile.
    self.temp_key_map tells program which keyname to use for which widget.
    """
    def widget_update_tempfile(self, widget):
        key = self.temp_key_map[widget]
        d = {}
        d[key] = widget.get()
        # only update the tempfile with these values if it is not empty, and is a valid float.
        if d[key] != "":
            try:
                float(d[key])
                update_temp(TEMPMANAGER_MANAGER.files[m1f1], d)
            except ValueError:
                pass
    

"""
Widget controlling the amount of steps and the starting timestep.
Also gives an additonal option for the choice of timestep scaling (and their associated params)
"""
class TimeStep_n_NumStep():
    '''
    screw it, i'm gonna make classes for everything. Why not
    '''
    simTime:float
    simVar:tk.StringVar

    responses = {
        "good" : "everything looks good!",
        "bad" : "dt is too big."
    }

    def __init__(self, master):
        self.master = master

        self.frame = tk.Frame(self.master, borderwidth=2, relief=tk.SUNKEN)
        self.frame.grid(row=0, column=0, sticky="NSEW")
        #self.master.grid_columnconfigure(0, weight=1)

        # holds the bob checkbox
        self.frame0 = tk.Frame(self.frame)
        self.frame0.grid(row=0, column=0, rowspan=3, columnspan=1, sticky="nsew")

        # Frame for holding dt, np entries
        self.frame2 = tk.Frame(self.frame)
        self.frame2.grid(row=0, column=2, sticky="w")

        # Frame for holding bob dt widgets
        self.frame1 = tk.Frame(self.frame)
        self.frame1.grid(row=2, column=2, sticky='w')

        # vertical separator
        separator = ttk.Separator(self.frame, orient='vertical')
        separator.grid(row=0, column=1, rowspan=3, sticky="ns")

        # horizontal separator
        separator2 = ttk.Separator(self.frame, orient="horizontal")
        separator2.grid(row=1, column=0, columnspan=3, sticky="ew")
        separator3 = ttk.Separator(self.frame, orient="horizontal")
        separator3.grid(row=3, column=0, columnspan=3, sticky="ew")

        # widget info
        self.do_bob = tk.IntVar()

        self.dt_do_bob = tk.Checkbutton(self.frame0, text="bob", variable=self.do_bob)
        tk.Label(self.frame0, text="").grid(row=0, column=0, rowspan=1, sticky="ew")
        tk.Label(self.frame0, text="").grid(row=1, column=0, rowspan=1, sticky="ew")
        self.dt_do_bob.grid(row=2, column=0, sticky="s", rowspan=1)

        self.do_bob_widgets = bob_dt_widget(self.frame1)
        self.do_bob_widgets.grid(row=0, column=0, sticky='w')
        self.do_bob.trace_add('write', partial(self.do_bob_widgets.toggle_editability, self.do_bob))

        self.dt_str = tk.StringVar()
        self.dt_label = tk.Label(self.frame,
                                 textvariable=self.dt_str)
        self.dt_label.grid(row=4, column=2)

        self.dt = LabeledEntry(self.frame2, val=0.0000001, row=1, col=0, col_span=1, title="Timestep (sec): ", width = 20, justify='center')
        self.dt.value.trace_add("write", self._Total_Sim_Time)
        self.dt.value.trace_add("write", self.dt_Callback)
        self.do_bob.trace_add("write", self.update_do_bob)
        
        self.numsteps = LabeledEntry(self.frame2, val=50000, row=0, col=0, col_span=1, title="Num Steps: ", width = 20, justify='center')
        self.numsteps.value.trace_add("write", self._Total_Sim_Time)
        self.numsteps.value.trace_add("write", self.update_numsteps)

        # display the simulation time
        self.simFrame = tk.Frame(self.master, bg="gray")
        self.simFrame.grid(row=0, column=1, sticky="NWES", columnspan=3)
        #self.simFrame.grid_rowconfigure(0, weight=1)
        #self.simFrame.grid_columnconfigure(0, weight=1)

        self.simVar = tk.StringVar()
        self._Total_Sim_Time()
        self._simLabel = tk.Label(self.simFrame,
                                  text="Total time (if constant): ")
        self.simLabel = tk.Label(self.simFrame,
                                 textvariable=self.simVar,
                                 justify="left")

        self.ref_p_var = tk.StringVar()
        self._ref_p_location = tk.Label(self.simFrame,
                                        text="Ref. particle position: ")
        self.ref_p_location = tk.Label(self.simFrame,
                                       textvariable=self.ref_p_var,
                                       justify='left')

        self.ref_dt_min_var = tk.StringVar()
        self._ref_dt_min = tk.Label(self.simFrame,
                                        text="dt min: ")
        self.ref_dt_min = tk.Label(self.simFrame,
                                       textvariable=self.ref_dt_min_var,
                                       justify='left')

        self.ref_dt_max_var = tk.StringVar()
        self._ref_dt_max = tk.Label(self.simFrame,
                                        text="dt max: ")
        self.ref_dt_max = tk.Label(self.simFrame,
                                       textvariable=self.ref_dt_max_var,
                                       justify='left')

        self._simLabel.grid(row=0, column=0, padx=5, pady=3)
        self.simLabel.grid(row=0, column=1, sticky="", padx=5, pady=3)

        self._ref_p_location.grid(row=1, column=0, padx=5, pady=3)
        self.ref_p_location.grid(row=1, column=1, padx=5, pady=3)

        self._ref_dt_max.grid(row=2, column=0, padx=5, pady=3)
        self.ref_dt_max.grid(row=2, column=1, padx=5, pady=3)

        self._ref_dt_min.grid(row=3, column=0, padx=5, pady=3)
        self.ref_dt_min.grid(row=3, column=1, padx=5, pady=3)

            # configure columns to have the same width
        self.frame.grid_columnconfigure(2, weight=1, uniform='dt_entries')

        self.frame1.grid_columnconfigure(0,  weight=1, uniform='entries1')

        self.frame2.grid_columnconfigure(0, weight=1, uniform='entries1')
        self.frame2.grid_columnconfigure(1, weight=1, uniform='entries1')

        #table.lim.attach(self)
        #self.dt_Callback()
            # attach trace to the value of the numsteps entry to update the tempfile
        self.do_bob_widgets.var_ref_p.trace_add('write', self.get_ref_position)
        for w in self.do_bob_widgets.entries:
            w.bind('<KeyRelease>', partial(self.get_dt_consts, w, True))
        self.get_ref_position()
        self.get_dt_consts(None)

    """
    call the bob dt constants funcs
    """
    def get_dt_consts(self, widget, update=False, *args):
        #print(f"what")
        if update:
            self.do_bob_widgets.widget_update_tempfile(widget)
        consts = before_simulation_bob_dt()

        self.ref_dt_min_var.set(consts['bob_dt_min'])
        self.ref_dt_max_var.set(consts['bob_dt_max'])


    """
    get the location of the ref particle when bob_dt is used.
    """
    def get_ref_position(self, *args):
        c = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])[param_keys.field_methods.name]['b']['params']['collection'][0].position
        pos = c * self.do_bob_widgets.var_ref_p.get()
        self.ref_p_var.set(str(pos))
        return pos

    """
    Necessary for the observer pattern to work; a function of this name is expected to exist for all event subs
    """
    def update(self, *args):
        """
        when the 'lim' Data in the current table is updated, you have to re-run the Dt size check.
        """
        self.dt_Callback()
        self.get_ref_position()
        self.get_dt_consts(None)

    def update_numsteps(self, *args):
        try:
            d = {param_keys.numsteps.name : int(self.numsteps.entry.get())}
            self.update_tempfile(d)
        except:
            pass

    def update_tempfile(self, updates):
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1]) | (updates)
        #print(d)
        write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

    def update_do_bob(self, *args):
        d = {param_keys.dt_bob.name : int(self.do_bob.get())}
        self.update_tempfile(d)

    def update_dt(self, *args):
        self.update_tempfile({"dt": float(self.dt.entry.get())})

    def dt_Callback(self, *args):
        #print(f"dt_callback called")
        try:
            lim = self._Check_Timestep_Size()
            self.update_dt()
            if float(self.dt.value.get()) < lim:
                self.dt_str.set(self.responses["good"])
            else:
                self.dt_str.set(f'Dt is too big, upper lim is: {lim}')
        except:
            pass
        
    
    def _Total_Sim_Time(self, *args):
        dt = self.dt.value.get()
        numsteps = self.numsteps.value.get()


        if(_Try_Float([dt, numsteps])):
            dt = float(dt)
            numsteps = float(numsteps)

            self.simTime = dt * numsteps
            self.simVar.set(str(self.simTime))
            return True
        return False
    
    def GetData(self):
        '''
        returns relevant data in a readable format
        '''
        data = {}
        data["numsteps"] = float(self.numsteps.entry.get())
        data["dt"] = float(self.dt.entry.get())
        data["dt_bob"] = int(self.do_bob.get())
        return data
    
    def _Set(self, key:str, value:list):
        match key:
            case 'numsteps':
                self.numsteps.value.set(value)
            case 'timestep':
                self.dt.value.set(value)

    def _first_coil_max(self):
        # extract the thing.
        coils = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
        #print(coils)
        return np.max(abs(coils[param_keys.mag_coil.name][0].position))
    
    def _Check_Timestep_Size(self):
        """
        make sure that the timestep is sufficient.
        """
        distance = self._first_coil_max() * 2 #Assuming that the coils are symmetric about origin
        #print(distance)
        desired_steps = 100
        desired_rate = 10e6

        dt_lim = distance/(desired_steps * desired_rate)
        
        return dt_lim
    
    """
    Called during the Init_GUI event.
    """
    def init_temp(self, lu):
        if lu is not None:
            try:
                self._Set('numsteps', lu[param_keys.numsteps.name])
                self._Set('timestep', lu[param_keys.dt.name])
                
                self.do_bob_widgets.var_ref_p.set(value=lu[param_keys.dt_bob_prop.name])
                self.do_bob_widgets.var_dyn_r.set(value=lu[param_keys.dt_bob_dyn_rng.name])
            except KeyError:
                self._Set('numsteps', 100000)
                self._Set('timestep', 2.2e-9)

                self.do_bob_widgets.var_ref_p.set(value=0)
                self.do_bob_widgets.var_dyn_r.set(value=10)
        self.update_do_bob()
        self.update_numsteps()
        self.dt_Callback()
        self.update_dt()
        self.do_bob_widgets.toggle_editability(self.do_bob)
import tkinter as tk
from tkinter import ttk
import numpy as np
from bokeh.layouts import column

from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Gui_tkinter.widgets.BorisGuiClasses import _Try_Float

#from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp, update_temp
#from system.temp_file_names import manager_1, m1f1, param_keys
from functools import partial

from Gui_tkinter.widgets.base import ParamWidget
from events.funcs import before_simulation_bob_dt

from system.state_dict_main import AppConfig
from system.state_dict import DynDtConfig

"""
Associated params for the bob timestep scaling.
    > reference proportion (0: origin, 1: circle's center): Scale from 0 to 1. Determines where on the line to place the ref. particle
    > dynamic range (float): factor for how low/high to look for dtp
"""
class bob_dt_widget(tk.Frame, ParamWidget):
    def __init__(self, master, params, borderwidth=2, relief=tk.SUNKEN):

        super().__init__(master)
            # information-holding widgets
                # titles
        self._ref_p = tk.Label(self, text="Reference Proportion: ", justify='left')
        self._dyn_r = tk.Label(self, text="Dynamic Range: ", justify='left')
                
                # entries (var, widget, and event binding)
        self.var_ref_p = tk.DoubleVar(value=params.step.dynamic.proportion)
        self.var_dyn_r = tk.DoubleVar(value=params.step.dynamic.dynamic_range)
        self.ref_p = tk.Entry(self, textvariable=self.var_ref_p, justify='center')
        self.dyn_r = tk.Entry(self, textvariable=self.var_dyn_r, justify='center')
        self.ref_p.bind("<KeyRelease>", partial(self.set_nested_field, params,
                                                "step.dyamic.proportion", self.ref_p))
        self.dyn_r.bind("<KeyRelease>", partial(self.set_nested_field, params,
                                                "step.dynamic.dynamic_range", self.dyn_r))

                # PACKING
        self._ref_p.grid(row=0, column=0, sticky='w')
        self.ref_p.grid(row=0, column=1, sticky='e')
        self._dyn_r.grid(row=1, column=0, sticky='w')
        self.dyn_r.grid(row=1, column=1, sticky='e')
    
            # meta info
                # container for state handling (toggle editability)
        self.entries = [self.ref_p, self.dyn_r]
                # mapping to be used in update function
        #self.temp_key_map = {self.ref_p : param_keys.dt_bob_prop.name,
        #                     self.dyn_r : param_keys.dt_bob_dyn_rng.name}
    
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

    def __init__(self, master, params:AppConfig):
        self.params = params

        #self.check_last()

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

        self.do_bob_widgets = bob_dt_widget(self.frame1, params)
        self.do_bob_widgets.grid(row=0, column=0, sticky='w')
        self.do_bob.trace_add('write', partial(self.do_bob_widgets.toggle_editability, self.do_bob))

        self.dt_str = tk.StringVar()
        self.dt_label = tk.Label(self.frame,
                                 textvariable=self.dt_str)
        self.dt_label.grid(row=4, column=2)

        self.dt = LabeledEntry(self.frame2, val=self.params.step.dt, row=1, col=0, col_span=1, title="Timestep (sec): ", width = 20, justify='center')
        self.dt.value.trace_add("write", self._Total_Sim_Time)
        self.dt.value.trace_add("write", self.dt_Callback)
        self.do_bob.trace_add("write", self.update_do_bob)
        
        self.numsteps = LabeledEntry(self.frame2, val=self.params.step.numsteps, row=0, col=0, col_span=1, title="Num Steps: ", width = 20, justify='center')
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
        #self.get_ref_position()
        #self.get_dt_consts(None)

    """
    call the bob dt constants funcs
    """
    def get_dt_consts(self, widget, update=False, *args):
        #if update:
            #self.do_bob_widgets.widget_update_tempfile(widget)
        consts = before_simulation_bob_dt(params=self.params)

        self.ref_dt_min_var.set(consts['bob_dt_min'])
        self.ref_dt_max_var.set(consts['bob_dt_max'])


    def get_ref_position(self, *args):
        """
        get the location of the ref particle when bob_dt is used.
        """

        if self.params.b.method != 'zero':
            c = self.params.b.collection[0].position
            pos = c * self.do_bob_widgets.var_ref_p.get()
            self.ref_p_var.set(str(pos))
            return pos

        return np.zeros(3)

    """
    Necessary for the observer pattern to work; a function of this name is expected to exist for all event subs
    """
    def update_bob_dt(self, *args):
        """
        This specific update is only run when bob_dt's checkmark is toggled
        """
        if self.params.b.method != 'zero':
            self.get_ref_position()
            self.get_dt_consts(None)


    def update(self, force_update=False, *args):
        """
        when the 'lim' Data in the current table is updated, you have to re-run the Dt size check.
        """
        self.dt_Callback()
        self.update_dt()
        # update bob_dt params if needed
        if self.do_bob.get() != 0 | force_update:
            self.update_do_bob()

    def update_numsteps(self, *args):
        self.params.step.numsteps = int(self.numsteps.entry.get())


    def update_do_bob(self, *args):
        """
        toggle the do_bob option on or off.
        """
        v = int(self.do_bob.get()) #0 or 1; the value of the checkbox after getting toggled.

        if v == 1:
            self.params.step.dynamic.on = True
            self.update_bob_dt()
        else:
            self.params.step.dynamic.on = False

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
        coils = self.params.b.collection
        #print(coils)
        return np.max(abs(coils[0].position))
    
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
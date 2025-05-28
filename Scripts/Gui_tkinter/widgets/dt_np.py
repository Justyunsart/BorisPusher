import tkinter as tk
import numpy as np

from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Gui_tkinter.widgets.BorisGuiClasses import _Try_Float

from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import manager_1, m1f1, param_keys

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

        self.frame = tk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="NSEW")
        self.master.grid_columnconfigure(0, weight=1)
        
        # Frame for holding check warning
        self.frame1 = tk.Frame(self.frame)
        self.frame1.grid(row=4, column=0)
        
        self.do_bob = tk.IntVar()

        self.dt_do_bob = tk.Checkbutton(self.frame1, text="bob", variable=self.do_bob)
        self.dt_do_bob.grid(row=0, column=0)

        self.dt_str = tk.StringVar()
        self.dt_label = tk.Label(self.frame1,
                                 textvariable=self.dt_str)
        self.dt_label.grid(row=1, column=0)

        self.dt = LabeledEntry(self.frame, val=0.0000001, row=1, title="Timestep (sec): ", width = 10)
        self.dt.value.trace_add("write", self._Total_Sim_Time)
        self.dt.value.trace_add("write", self.dt_Callback)
        self.do_bob.trace_add("write", self.update_do_bob)
        
        self.numsteps = LabeledEntry(self.frame, val=50000, row=0, title="Num Steps: ", width = 10)
        self.numsteps.value.trace_add("write", self._Total_Sim_Time)
        self.numsteps.value.trace_add("write", self.update_numsteps)

        # display the simulation time
        self.simFrame = tk.LabelFrame(self.master, text="Total Sim Time: ", bg="gray")
        self.simFrame.grid(row=0, column=1, sticky="NWES")
        self.simFrame.grid_rowconfigure(0, weight=1)
        self.simFrame.grid_columnconfigure(0, weight=1)

        self.simVar = tk.StringVar()
        self._Total_Sim_Time()
        self.simLabel = tk.Label(self.simFrame,
                                 textvariable=self.simVar,
                                 justify="center")
        self.simLabel.grid(row=0, column=0, sticky="")

        #table.lim.attach(self)
        #self.dt_Callback()
            # attach trace to the value of the numsteps entry to update the tempfile

    """
    Necessary for the observer pattern to work; a function of this name is expected to exist for all event subs
    """
    def update(self, *args):
        """
        when the 'lim' Data in the current table is updated, you have to re-run the Dt size check.
        """
        self.dt_Callback()

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

    def dt_Callback(self, *args):
        #print(f"dt_callback called")
        try:
            lim = self._Check_Timestep_Size()
            self.update_tempfile({"dt": float(self.dt.entry.get())})
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
            except KeyError:
                pass
        self.update_do_bob()
        self.update_numsteps()
        self.dt_Callback()
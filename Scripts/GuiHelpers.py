from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from BorisPlots import graph_trajectory
from GuiEntryHelpers import Dict_to_CSV
import os
from dataclasses import dataclass

from PrefFile import PrevFiles
import pandas as pd
import csv

from magpy4c1 import runsim


'''
File explorer for restart files
'''
inpd=""
# Variable to store the dir of the input file
def browseFiles(name:ttk.Label):
    filename = filedialog.askopenfilename(title = "Select a Restart File")
    if(filename != ""): # If an actual file is selected
        name.configure(text = filename)
        inpd = filename
    return True

def PlotFileCallback(name:ttk.Label, button:ttk.Button):
    FileCallback(browseFiles(name), button)

def PlotConfirmCallback(name:ttk.Label, root:Tk):
    graph_trajectory(lim = 500, data = name.cget("text"))
    #root.quit()


# HELPERS
'''
Display Timestep Widget
'''
def CalcTimestep(time, numsteps):
    ## Display Calculated Timestep
    v = (time.get()) / (numsteps.get())
    return v

'''
Update Timestep value and label in the GUI when numsteps/sim time are updated
'''
def DTcallback(entry_sim_time_value, entry_numsteps_value, label_time_step:ttk.Label):
    time_step_value = CalcTimestep(entry_sim_time_value, entry_numsteps_value)
    label_time_step.configure(text = "Timestep: " + str(time_step_value))
    return time_step_value

'''
Toggles
'''
def RestartFile(cond:BooleanVar, button_restart_file:ttk.Button):
    cond = cond.get()
    print(cond)
    FileCallback(cond, button_restart_file)

def FileCallback(do_file:bool, button_restart_file:ttk.Button):
    if(do_file == False):
        #print("button disabled")
        button_restart_file.configure(state = "disabled")
        return True
    else:
        #print("button enabled")
        button_restart_file.configure(state = "enabled")
        return True
    

'''
value: the string name of the method of field calculation

This field callback runs every time a value is selected from a field GUI's dropdown.

It should:
    > make the X, Y, Z entry boxes in the details frame active, if it's "static"
    > make these values 0 if it's either "zeros" or "calculate", and disable.
    
'''
def FieldCallback(event, value:ttk.Combobox, xcontainer:Entry, ycontainer:Entry, zcontainer:Entry):
    value = value.get()
    match value:
        case "Zero" | "Calculated":
            #print("case in 1")
            #print(value)
            xcontainer.config(state="disabled",
                              text = "0.0")
            ycontainer.config(state="disabled",
                              text = "0.0")
            zcontainer.config(state="disabled",
                              text = "0.0")
        case "Static":
            #print("case in 2")
            #print(value)
            xcontainer.config(state="normal",
                              text = "0.0")
            ycontainer.config(state="normal",
                              text = "0.0")
            zcontainer.config(state="normal",
                              text = "0.0")

def CSV_to_Df(dir, isNum=True):
    '''
    A function that will be called in the calculate button's command.
    Turns the csv data in the particle input file to a workable dataframe.

    dir: path to the file to be read.
    isNum: a bool that determines if everything should be considered numeric or not.
    '''
    # step 1: read the file from the directory.
    data = pd.read_csv(dir)
    #print(data)

    # step 2: numeric checks
    ## does not iterate if the entire df is numeric.
    if (isNum):
        data.apply(pd.to_numeric)
    ## iterates through columns if the entire dataframe is not numeric.
    else:
        for col in data:
            try:
                data[col] = data[col].astype(float)
            except ValueError:
                pass
    #print(data)
    return data

# Run the simulation if you press calculate

# TODO: Add functionality for tracking last used conditions
def CalculateCallback(params:list, DIR_last:str):
    '''
    When the calculate button is pressed, the GUI passes key information to
    the backend and starts the simulation.
    '''
    data = GatherParams(params)
    toProgram = {
        'numsteps' : data['numsteps'],
        'timestep' : data['dt'],
        'coils' : data['coils'],
        'doStaticB' : data['B-Field_Use'],
        'doStaticE' : data['E-Field_Use'],
        'B-Field' : data['B-Field'],
        'E-Field' : data['E-Field'],
        'particles':data["<class 'GuiEntryHelpers.file_particle'>"]
        }
    toFile = {
        'numsteps' : data['numsteps'],
        'timestep' : data['dt'],
        'coilFile' : data['Coil File'],
        'doStaticB' : data['B-Field_Use'],
        'doStaticE' : data['E-Field_Use'],
        'B-Field' : data['B-Field'],
        'E-Field' : data['E-Field'],
        'particleFile':data["Particle File"]
        }

    Dict_to_CSV(DIR_last, toFile, newline="")

    runsim(toProgram)


def GatherParams(params:list):
    '''
    obtain the current values of all relevant parameters.

    params: the list that keeps a reference to all relevant tkinter objects.
    '''
    data = {}
    for widget in params:
        x = widget.GetData()
        #print("x is: ", x)
        data = {**data, **x} # merge the resulting dictionaries to update the original data container
        #print("data updated to: ", data)
    return data

def FillWidgets(p:list, path:str):
    """
    takes a dictionary of parameter values, and fills the windows' widgets with their values.

    params: list
        > a list of all the widgets that need to be edited.
    values: str (path to dict)
        > Keys: the names of all the parameters
        > Values: the value to change these parameters to
    """
    values = {}
    with open(path, mode='r') as file:
        reader = csv.reader(file)

        keys = next(reader) # get first line
        vals = next(reader) # move to the second line

        for i in range(len(keys)):
            values[keys[i]] = vals[i]
    print(values)

    fieldWidgets = {
        'numsteps' : p[0],
        'timestep' : p[0],
        'coilFile' : p[2],
        'doStaticB' : FieldDict(p[3], 0),
        'doStaticE' : FieldDict(p[4], 0),
        'B-Field' : FieldDict(p[3], 1),
        'E-Field' : FieldDict(p[4], 1),
        'particleFile': p[1]
        }
    
    for key, value in fieldWidgets.items():
        """
        for every field, run their respective widgets' setter functions.
        """
        value._Set(key, values[key])

class FieldDict():
    def __init__(self, inst, val):
        self.out = {}
        self.out["param"] = inst
        self.out["id"] = val

    def _Set(self, fieldName, val):
        " remember, val here is from the input data file"
        match self.out["id"]:
            case 0:
                self.out["param"].SetCheck(val)
            case 1:
                self.out["param"].SetCoords(val)


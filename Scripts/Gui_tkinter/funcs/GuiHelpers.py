from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from BorisPlots import graph_trajectory
from Gui_tkinter.funcs.GuiEntryHelpers import Dict_to_CSV

import pandas as pd
import csv

from calcs.magpy4c1 import runsim
from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import manager_1, m1f1
from events.events import Events

import threading
from multiprocessing import Manager

from Gui_tkinter.widgets.progress_window import calculate_progress_window
from events.events import Events

'''
File explorer for restart files
'''
inpd=""

def updateTempFile(updates):
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
        d.update(updates)
        write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)


# Variable to store the dir of the input file
def browseFiles(name:StringVar, dir):
    """
    Opens the file browser, expects users to select a file.
    """
    filename = filedialog.askopenfilename(title = "Select a Restart File",
                                          initialdir = dir)
    if(filename != ""): # If an actual file is selected
        name.set(filename)
        #print(name.get)
        inpd = filename
    return True

def PlotFileCallback(name:StringVar, dir):
    """
    called from BorisGui when outpout file browsing is pressed.
    First calls browseFiles to prompt user for file.
    Then, FileCallback is called to enable the plot button (which is disabled by default)
    """
    Events.PRE_PLOT.value.invoke() # run extra event logic (creating the tempfile for plotting)
    browseFiles(name, dir)

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
        button_restart_file.configure(state = "normal")
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

# Run the simulation if you press calculate

def CalculateCallback(params:list, DIR_last:str, root, manager):
    '''
    When the calculate button is pressed, the GUI passes key information to
    the backend and starts the simulation.
    '''
    Events.PRE_CALC.value.invoke()
    data = GatherParams(params)
    toProgram = {
        'numsteps' : data['numsteps'],
        'timestep' : data['dt'],
        'coils' : data['coils'],
        'B-Field' : data['B_Methods'],
        'E-Field' : data['E_Methods'].GetData(),
        'particles':data["<class 'Gui_tkinter.funcs.GuiEntryHelpers.file_particle'>"],
        "Coil File" : data["Coil File"]
        }
    #print(toProgram)
    toFile = {
        'numsteps' : data['numsteps'],
        'timestep' : data['dt'],
        'coilFile' : data['Coil File'],
        'B-Field' : data['B_Methods'],
        'E-Field' : data['E_Methods'].GetData(),
        'particleFile':data["Particle File"]
        }

    Dict_to_CSV(DIR_last, toFile, newline="")
    
        # add some last minute info to the tempfile
    updateTempFile({"Field_Methods" : {"B" : data["B_Methods"], "E" : data["E_Methods"].GetData()},
                    "Particle_Df" : data["<class 'Gui_tkinter.funcs.GuiEntryHelpers.file_particle'>"],
                    "coil_file_name" : data["Coil File"]})

    #####################################################################################
    # STUFF FOR THE PROGRESS WINDOW (WHICH NEEDS RUNTIME DATA)
        # a multiprocessing manager wraps the thread that creates the processpool.
    queue = manager.Queue()
    progress = calculate_progress_window(root, queue)
    process_thread = threading.Thread(target=runsim, args=(toProgram, queue,), daemon=True)
    process_thread.start()
    progress.poll_queue()


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
    try:
        with open(path, mode='r') as file:
            reader = csv.reader(file)

            keys = next(reader) # get first line
            vals = next(reader) # move to the second line

            for i in range(len(keys)):
                values[keys[i]] = vals[i]
        #print(values)
        # update tempfile
        updateTempFile(values)

        fieldWidgets = {
            'numsteps' : p[0],
            'timestep' : p[0],
            'coilFile' : p[2],
            'B-Field' : p[3],
            'E-Field' : p[4],
            'particleFile': p[1]
            }
        
        for key, value in fieldWidgets.items():
            """
            for every field, run their respective widgets' setter functions.
            """
            value._Set(key, values[key])
        return True
    except:
        return False
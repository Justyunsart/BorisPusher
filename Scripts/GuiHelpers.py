from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from BorisPlots import graph_trajectory

'''
File explorer for restart files
'''

# Variable to store the dir of the input file
def browseFiles(name:ttk.Label):
    filename = filedialog.askopenfilename(title = "Select a Restart File")
    inpd = filename
    if(filename != ""): # If an actual file is selected
        name.configure(text = filename)
    return True

def PlotFileCallback(name:ttk.Label, button:ttk.Button):
    FileCallback(browseFiles(name), button)

def PlotConfirmCallback(name:ttk.Label, root:Tk):
    graph_trajectory(lim = 500, data = name.cget("text"))
    root.destroy()


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
def FileCallback(do_file:bool, button_restart_file:ttk.Button):
    if(not do_file):
        # print("button disabled")
        button_restart_file.configure(state = "disabled")
        return True
    else:
        # print("button enabled")
        button_restart_file.configure(state = "enabled")
        return True
    
# Run the simulation if you press calculate
def CalculateCallback(isRun:BooleanVar, root:Tk):
    isRun.set(True)
    root.destroy()

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
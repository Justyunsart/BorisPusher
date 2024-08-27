from tkinter import *
from tkinter import filedialog
from tkinter import ttk

'''
File explorer for restart files
'''

# Variable to store the dir of the input file
inpd = ""
def browseFiles(button:ttk.Button):
    filename = filedialog.askopenfilename(title = "Select a Restart File")
    button.configure(text = filename)
    inpd = filename

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
def FileCallback(do_file:BooleanVar, button_restart_file:ttk.Button):
    if(do_file.get() == False):
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
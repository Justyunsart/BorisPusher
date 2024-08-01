from tkinter import *
from tkinter import filedialog
from tkinter import ttk

#######
# GUI #
#######
'''
Testing the code by changing parameters and numsteps and everything became too cumbersone, so I decided to
bite the bullet and create some GUI for it. 
'''

# Application Window
root = Tk()
root.title("Configure Sim")

# Content Frame
#    > Holds contents of the UI
mainframe = ttk.Frame(root, padding = "3 3 12 12")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

rframe = ttk.Frame(root, padding = "3 3 12 12")
rframe.grid(column=1, row=0, sticky = (N, W, E, S))

#======#
# MENU #
#======#
# CREATION
menubar = Menu(root)

# FILE TAB
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=file)
## commands
file.add_command(label="Preferences")

## helpers
def PrefCallback():
    # TODO: Create a popup window that allows users to set default output dirs and other options.
    return 0

#=============#
# GUI WIDGETS #
#=============#
# HELPERS

'''
File explorer for restart files
'''

# Variable to store the dir of the input file
inpd = ""
def browseFiles():
    filename = filedialog.askopenfilename(title = "Select a Restart File")
    button_restart_file.configure(text = filename)
    inpd = filename

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
def DTcallback():
    global time_step_value
    val = CalcTimestep(entry_sim_time_value, entry_numsteps_value)
    time_step_value = val
    label_time_step.configure(text = "Timestep: " + str(val))
    return True

'''
Toggles
'''
def FileCallback():
    if(do_file.get() == False):
        # print("button disabled")
        button_restart_file.configure(state = "disabled")
        return True
    else:
        # print("button enabled")
        button_restart_file.configure(state = "enabled")
        return True

# WIDGETS
## Display terminal output?
doDisplay = BooleanVar(value = True)
checkDisplay = ttk.Checkbutton(mainframe,
                               text = "Crap in Terminal?",
                               variable = doDisplay,
                               onvalue = True,
                               offvalue = False)

## Read restart file?
do_file = BooleanVar(value = False)
check_restart_file = ttk.Checkbutton(mainframe,
                                     variable = do_file,
                                     text = "Read Input File?",
                                     onvalue = True,
                                     offvalue = False,
                                     command = FileCallback)


label_restart_file = ttk.Label(mainframe,
                               text = "Restart File Dir:").grid(column = 0, row = 1, sticky=(W))
button_restart_file = ttk.Button(mainframe,
                                 text = "Browse Files",
                                 command = browseFiles)
button_restart_file.grid(column = 1, row = 1)

### Make sure the button is in the correct state to start
FileCallback()

## Numsteps
label_numsteps = ttk.Label(mainframe,
                           text = "Number of Steps: ").grid(column = 0, row = 3)

entry_numsteps_value = IntVar(value = 500000)
entry_numsteps = ttk.Entry(mainframe,
                           textvariable = entry_numsteps_value,
                           validate = "focusout",
                           validatecommand = DTcallback)
entry_numsteps.grid(column = 1, row = 3)

## Total Time to Simulate - Simulation Time
label_sim_time = ttk.Label(mainframe,
                           text = "Sim Time: ").grid(column = 0, row = 4)
entry_sim_time_value = DoubleVar(value = 20.0)
entry_sim_time = ttk.Entry(mainframe,
                           textvariable = entry_sim_time_value,
                           validate = "focusout",
                           validatecommand = DTcallback).grid(column = 1, row = 4)

## Display Calculated Timestep
time_step_value = (entry_sim_time_value.get()) / (entry_numsteps_value.get())
label_time_step = ttk.Label(rframe,
                            text = "Time step: " + str(time_step_value))
## Caclulate button
button_calculate = ttk.Button(mainframe,
                              text = "Calculate",
                              command = root.destroy) # Close the window so the rest of the program can run

# Display the widgets
for w in mainframe.winfo_children():
    w.grid_configure(padx = 5, pady = 5)
for w in rframe.winfo_children():
    w.grid_configure(padx=5,pady=5)
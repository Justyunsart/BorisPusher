from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from GuiHelpers import *
from functools import partial

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
# mainframe = ttk.Frame(root, padding = "3 3 12 12")
# mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
# root.columnconfigure(0, weight = 1)
# root.rowconfigure(0, weight = 1)

#rframe = ttk.Frame(root, padding = "3 3 12 12")
#rframe.grid(column=1, row=0, sticky = (N, W, E, S))

#======#
# MENU #
#======#

# PLOT OR CALCULATE?
tabControl=ttk.Notebook(root, padding="4 12 12 4", width=800, height=400)

## Create tab objects
tab_calc = ttk.Frame(tabControl, padding="4 12 12 4")
#tab_calc.grid(column = 0, row = 0, sticky = (N, W, E, S))
#tab_calc.columnconfigure(0, weight = 1)
#tab_calc.rowconfigure(0, weight = 1)

tab_plot = ttk.Frame(tabControl, padding="4 12 12 4")

## Add tab objects to notebook
tabControl.add(tab_calc, text="Calculate")
tabControl.add(tab_plot,text="Plot")
tabControl.pack(expand=1, fill="both")

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


# PLOT GUI #
#=============#
# GUI WIDGETS #
#=============#

label_out_file = ttk.Label(tab_plot,
                               text = "Output File Dir:")#.grid(column = 0, row = 1, sticky=(W))
button_out_file = ttk.Button(tab_plot,
                                 text = "Browse Files")



# CALCULATION GUI#

#=============#
# GUI WIDGETS #
#=============#
# WIDGETS
## Display terminal output?
doDisplay = BooleanVar(value = True)
checkDisplay = ttk.Checkbutton(tab_calc,
                               text = "Crap in Terminal?",
                               variable = doDisplay,
                               onvalue = True,
                               offvalue = False)

## Read restart file?
do_file = BooleanVar(value = False)

button_restart_file = ttk.Button(tab_calc,
                                 text = "Browse Files")
button_restart_file.config(command=partial(browseFiles, button_restart_file))

check_restart_file = ttk.Checkbutton(tab_calc,
                                     variable = do_file,
                                     text = "Read Input File?",
                                     onvalue = True,
                                     offvalue = False)
check_restart_file.config(command=partial(FileCallback, do_file, button_restart_file))


label_restart_file = ttk.Label(tab_calc,
                               text = "Restart File Dir:")#.grid(column = 0, row = 1, sticky=(W))

#button_restart_file.grid(column = 1, row = 1)

### Make sure the button is in the correct state to start
FileCallback(do_file, button_restart_file)


## Numsteps
label_numsteps = ttk.Label(tab_calc,
                           text = "Number of Steps: ")#.grid(column = 0, row = 3)

entry_numsteps_value = IntVar(value = 500000)
entry_sim_time_value = DoubleVar(value = 20.0)

## Display Calculated Timestep
time_step_value = (entry_sim_time_value.get()) / (entry_numsteps_value.get())
label_time_step = ttk.Label(tab_calc,
                            text = "Time step: " + str(time_step_value))

entry_numsteps = ttk.Entry(tab_calc,
                           textvariable = entry_numsteps_value,
                           validate = "focusout")
entry_numsteps.configure(validatecommand=partial(DTcallback, entry_sim_time_value, entry_numsteps_value, label_time_step))
#entry_numsteps.grid(column = 1, row = 3)

## Total Time to Simulate - Simulation Time
label_sim_time = ttk.Label(tab_calc,
                           text = "Sim Time: ")#.grid(column = 0, row = 4)
entry_sim_time = ttk.Entry(tab_calc,
                           textvariable = entry_sim_time_value,
                           validate = "focusout")#.grid(column = 1, row = 4)
entry_sim_time.config(validatecommand=partial(DTcallback, entry_sim_time_value, entry_numsteps_value, label_time_step))

## Caclulate button
isRun = BooleanVar(value=False)

    
button_calculate = ttk.Button(tab_calc,
                              text = "Calculate") # Close the window so the rest of the program can run
button_calculate.config(command=partial(CalculateCallback, isRun, root))

# Display the widgets
for w in tab_calc.winfo_children():
    w.grid_configure(padx = 5, pady = 5)
#for w in rframe.winfo_children():
#    w.grid_configure(padx=5,pady=5)
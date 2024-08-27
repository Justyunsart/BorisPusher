from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
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
tabControl=ttk.Notebook(root, padding="4 12 12 4", width=400, height=400)

## Create tab objects
tab_calc = tk.Frame(tabControl)
tab_calc.grid(column = 0, row = 0, sticky = (N, W, E, S))
tab_calc.columnconfigure(0, weight = 1)
tab_calc.rowconfigure(1, weight = 1)

tab_plot = ttk.Frame(tabControl, padding="4 12 12 4")


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
name_out_file = ttk.Label(tab_plot,
                          text="No Output File Selected")
button_out_file.config(command=partial(browseFiles, name_out_file))



# CALCULATION GUI#

#=============#
# GUI WIDGETS #
#=============#
# WIDGETS
## Display terminal output?

#tab_calc.grid_columnconfigure(0, weight=1)
#tab_calc.grid_rowconfigure(0, weight=1)

style = ttk.Style()
style.configure("LG.TCheckbutton", background="light gray", foreground="black", indicatorbackground="black", indicatorforeground="white")

# FRAMES

## MAIN CONTAINER
calc_title_LFrame = ttk.Labelframe(tab_calc,
                             text="Boris Push Calculation")
calc_title_LFrame.grid(row=1, pady=10, padx=10, sticky="N")

## SUB CONTAINERS
CalcContainer = tk.LabelFrame(calc_title_LFrame, bg="gray", text="Parameters")
CalcContainer.grid(row=3,column=0)

CalcCheckBoxFrame = tk.Frame(calc_title_LFrame, bg="light gray")
CalcCheckBoxFrame.grid(row=1, pady=5, padx=5, sticky="N")

CalcRestartFileFrame = tk.Frame(calc_title_LFrame)
CalcRestartFileFrame.grid(row=2, pady=5, padx=5)


CalcTimeStepFrame = tk.Frame(CalcContainer, bg="light gray")
CalcTimeStepFrame.grid(row=4, pady=5, padx=20)

doDisplay = BooleanVar(value = True)
checkDisplay = ttk.Checkbutton(CalcCheckBoxFrame,
                               text = "Crap in Terminal?",
                               variable = doDisplay,
                               onvalue = True,
                               offvalue = False,
                               style="LG.TCheckbutton")
checkDisplay.grid(row=0)


## Read restart file?

do_file = BooleanVar(value = False)

label_restart_file = ttk.Label(CalcRestartFileFrame,
                               text = "Restart File Dir:",
                               anchor=W,
                               justify=RIGHT)
label_restart_file.grid(row=1)

button_restart_file = ttk.Button(CalcRestartFileFrame,
                                 text = "Browse Files")
button_restart_file.grid(row=1, column=1)

name_restart_file = ttk.Label(CalcRestartFileFrame,
                              text="No Input File Selected")
name_restart_file.grid(row=1, column=2)

button_restart_file.config(command=partial(browseFiles, name_restart_file))

check_restart_file = ttk.Checkbutton(CalcCheckBoxFrame,
                                     variable = do_file,
                                     text = "Read Input File?",
                                     onvalue = True,
                                     offvalue = False,
                                     style="LG.TCheckbutton")
check_restart_file.config(command=partial(FileCallback, do_file, button_restart_file))
check_restart_file.grid(row=0, column=1)


#button_restart_file.grid(column = 1, row = 1)

### Make sure the button is in the correct state to start
FileCallback(do_file, button_restart_file)


## Numsteps
label_numsteps = ttk.Label(CalcTimeStepFrame,
                           text = "Number of Steps: ")#.grid(column = 0, row = 3)
label_numsteps.grid(row=2, column=0)

entry_numsteps_value = IntVar(value = 500000)
entry_sim_time_value = DoubleVar(value = 20.0)

## Display Calculated Timestep
time_step_value = (entry_sim_time_value.get()) / (entry_numsteps_value.get())
label_time_step = ttk.Label(CalcTimeStepFrame,
                            text = "Time step: " + str(time_step_value))
label_time_step.grid(row=2, column=4)

entry_numsteps = ttk.Entry(CalcTimeStepFrame,
                           textvariable = entry_numsteps_value,
                           validate = "focusout")
entry_numsteps.configure(validatecommand=partial(DTcallback, entry_sim_time_value, entry_numsteps_value, label_time_step))
entry_numsteps.grid(column = 1, row = 2)

## Total Time to Simulate - Simulation Time
label_sim_time = ttk.Label(CalcTimeStepFrame,
                           text = "Sim Time: ")
label_sim_time.grid(column = 0, row = 3)
entry_sim_time = ttk.Entry(CalcTimeStepFrame,
                           textvariable = entry_sim_time_value,
                           validate = "focusout")
entry_sim_time.grid(column = 1, row = 3)
entry_sim_time.config(validatecommand=partial(DTcallback, entry_sim_time_value, entry_numsteps_value, label_time_step))

## Caclulate button
isRun = BooleanVar(value=False)

    
button_calculate = ttk.Button(tab_calc,
                              text = "Calculate") # Close the window so the rest of the program can run
button_calculate.config(command=partial(CalculateCallback, isRun, root))
button_calculate.grid(sticky="S")


## Add tab objects to notebook
tabControl.add(tab_calc, text="Calculate")
tabControl.add(tab_plot,text="Plot")
tabControl.pack(expand=1, fill="both")

# Display the widgets

#for w in rframe.winfo_children():
#    w.grid_configure(padx=5,pady=5)
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
from GuiHelpers import *
from functools import partial
from PusherClasses import EfOptions, BfOptions
from CurrentGuiClasses import *
from BorisGuiClasses import *
#######
# GUI #
#######
'''
Testing the code by changing parameters and numsteps and everything became too cumbersone, so I decided to
bite the bullet and create some GUI for it. 

This is the main hub for the GUI, with many helper files providing classes and functions.
'''
# Container for all the information to pass to program:
params = []

# Application Window
root = Tk()
root.title("Configure Sim")

# main window
Main = MainWindow(root)
Main.grid(row=0, column=0, sticky=N+W+E)
Main.grid_rowconfigure(0, weight=1)
Main.grid_columnconfigure(0, weight=1)

#======#
# MENU #
#======#

# add the toolbar
mainToolbar = ConfigMenuBar(Main)

# Selected dirs for sims
Main_PrefFiles = Main.prefs
DIR_Particle = Main_PrefFiles.DIR_particle
DIR_Coil = Main_PrefFiles.DIR_coil
DIR_coilDefs = Main_PrefFiles.DIR_coilDefs

#print(DIR_Particle)

# PLOT OR CALCULATE?
tabControl=ttk.Notebook(Main, padding="4 12 12 4")
tabControl.grid(row=0, column=0, sticky=N+W+E+S)

## Create tab objects
tab_calc = tk.Frame(tabControl)
tab_calc.grid(column = 0, row = 0, sticky = (N, W, E, S))
tab_calc.grid_columnconfigure(0, weight = 1)
tab_calc.grid_rowconfigure(0, weight = 1)

tab_plot = ttk.Frame(tabControl, padding="4 12 12 4")
tab_plot.grid_columnconfigure(0, weight = 1)
tab_plot.grid_rowconfigure(0, weight = 1)


tabControl.grid_rowconfigure(0, weight=1)
tabControl.grid_columnconfigure(0, weight=1)
# PLOT GUI #
#=============#
# GUI WIDGETS #
#=============#
## SUBFRAMES
plot_title_LFrame = ttk.LabelFrame(tab_plot,
                                   text="Plotting")
plot_title_LFrame.grid(row=0, sticky="NWES", padx=10, pady=10)

plot_out_file = ttk.LabelFrame(plot_title_LFrame,
                               text="Data Source")
plot_out_file.grid(row = 0, padx=10, pady=10)


## WIDGETS
### Output Files
label_out_file = ttk.Label(plot_out_file,
                               text = "Output File Dir:")#.grid(column = 0, row = 1, sticky=(W))
label_out_file.grid(row = 0, column= 0, padx=10, pady=10)

button_out_file = ttk.Button(plot_out_file,
                                 text = "Browse Files")
button_out_file.grid(row = 0, column=1, pady=10)

name_out_file = ttk.Label(plot_out_file,
                          text="No Output File Selected")
name_out_file.grid(row = 0, column=2, pady=10)

#button_out_file.config(command=partial(browseFiles, name_out_file))

### Confirm Button
'''
We need to keep watch on the selected data file value, and ensure that this button is active only when
there is a valid data file selected.
'''
plot_confirm = ttk.Button(tab_plot,
                          text="Create Plot",
                          state="disabled")
button_out_file.config(command=partial(PlotFileCallback, name_out_file, plot_confirm))
plot_confirm.config(command=partial(PlotConfirmCallback, name_out_file, root))


plot_confirm.grid(sticky=S)



# CALCULATION GUI#

#=============#
# GUI WIDGETS #
#=============#

style = ttk.Style()
style.configure("LG.TCheckbutton", background="light gray", foreground="black", indicatorbackground="black", indicatorforeground="white")

# FRAMES


## MAIN CONTAINER
calc_title_LFrame = ttk.Labelframe(tab_calc,
                             text="Boris Push Calculation")
calc_title_LFrame.grid(row=0, column=0, pady=10, padx=10, sticky="NW")

### SUB CONTAINERS

CalcContainer = tk.LabelFrame(calc_title_LFrame, bg="gray", text="Parameters")
CalcContainer.grid(row=0,column=0)


CalcCheckBoxFrame = tk.Frame(calc_title_LFrame, bg="light gray")
CalcCheckBoxFrame.grid(row=1, column=0, pady=10, padx=10, sticky="N")

CalcRestartFileFrame = tk.Frame(calc_title_LFrame)
CalcRestartFileFrame.grid(row=2, column= 0, pady=10, padx=10)

Particle = tk.LabelFrame(calc_title_LFrame, text="Particle Conditions")
Particle.grid(row=0, column=1, sticky="W")

DropdownFrame = tk.Frame(Particle)
DropdownFrame.grid(row=0, column=0, sticky="W")

ParticlePreviewFrame = tk.Frame(Particle)
ParticlePreviewFrame.grid(row=1, column=0, sticky="W")

CalcTimeStepFrame = tk.LabelFrame(CalcContainer, bg="light gray", text="Time, Step")
CalcTimeStepFrame.grid(row=0, column=0, pady=5, padx=20)

Fields = tk.LabelFrame(CalcContainer, bg="light gray", text="Static Fields")
Fields.grid(row=1, column=0)



## Particle condition stuff..
Combobox_particle_file = Particle_File_Dropdown(DropdownFrame,
                                                dir=DIR_Particle)
particleCheckboxes = ParticlePreviewSettings(DropdownFrame)
particlePreview = ParticlePreview(ParticlePreviewFrame,
                                  Combobox_particle_file)

## Timestep stuff..
time_info = TimeStep_n_NumStep(CalcTimeStepFrame)

## FIELDS!!!!!!
b_field = CoordTable(Fields, title="B-Field")
b_field.grid(row=0, column=0)

e_field = CoordTable(Fields, title="E-Field")
e_field.grid(row=1, column=0)


## Caclulate button
calc_button = tk.Button(tab_calc,
                        text="Calculate")
calc_button.grid(row=2, column=0)


## Add tab objects to notebook
tabControl.add(tab_calc, text="Calculate")
tabControl.add(tab_plot,text="Plot")
tabControl.pack(expand=1, fill="both")

#===========================================================================================#
########################
# CURRENT MANIPULATION #
########################
'''
#the place to see and change the configuration of the magnetic coils.
#Will happen in a new window because why not
'''
root.update() # set info for positioning with other windows
toplevel = tk.Toplevel(root)

# toplevel positioning, based on the dimension and offset of the root window.
toplevel_offsetx, toplevel_offsety = root.winfo_x() + root.winfo_width(), root.winfo_y()
toplevel.geometry(f"+{toplevel_offsetx}+{toplevel_offsety}")

CurrentFrame = tk.LabelFrame(toplevel, text="Configure Current")
CurrentFrame.grid(row = 0, padx=10, pady=10)

#CurrentFile = tk.Frame(CurrentFrame)
#CurrentFile.grid(row=0, column=0)
#CurrentTable = tk.Frame(CurrentFrame)
#CurrentTable.grid(row=1, column=0)

#coil_file = Particle_File_Dropdown(CurrentFile, DIR_Coil)
#coil_table = CurrentEntryTable(CurrentTable, CircleCurrentConfig, coil_file)
coil_config = CurrentConfig(CurrentFrame, DIR_Coil, DIR_coilDefs)

#=======#
# FINAL #
#=======#

# control what classes to send over to the program by adding it to params
params = [time_info, particlePreview, coil_config.table, b_field, e_field]
calc_button.configure(command=partial(CalculateCallback, params)) # update calculate button's command after setting up params
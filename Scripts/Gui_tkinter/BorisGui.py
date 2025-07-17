from tkinter import ttk
import tkinter as tk
import settings.palettes as p
from functools import partial
import os
from events.events import Events # omg why did I name things like this
from Gui_tkinter.funcs.GuiEntryHelpers import Bob_e_Config_Dataclass, CircleCurrentConfig
from Gui_tkinter.widgets.dt_np import TimeStep_n_NumStep
from Gui_tkinter.funcs.GuiHelpers import *
from Gui_tkinter.widgets.BorisGuiClasses import *
from Gui_tkinter.widgets.ScrollableFrame import ScrollableFrame
from Gui_tkinter.widgets.PlottingWindow import PlottingWindowObj, on_main_notebook_tab_changed
from definitions import (DIR_ROOT, DIR_CONFIG, NAME_INPUTS, NAME_COILS, NAME_PARTICLES, NAME_lastUsed, NAME_OUTPUTS)
import configparser
from system.Observer import Data
from system.path import Path
from system.temp_file_names import param_keys
from settings.configs.funcs.config_reader import runtime_configs

from Gui_tkinter.widgets.notebook.widget import Field_Notebook
from Gui_tkinter.widgets.notebook.tab_content import *



# events
#from events.on_start import on_start

"""
This script is directly called when running main.py - the function OpenGUI() defined below assembles the tkinter GUI and runs its mainloop.
"""
def OpenGUI(manager):
    '''
    Testing the code by changing parameters and numsteps and everything became too cumbersone, so I decided to
    bite the bullet and create some GUI for it. 
    This is the main hub for the GUI, with many helper files providing classes and functions.
    '''
    # Initialization checks. Run them.
    Events.ON_START.value.invoke()
    Events.PRE_INIT_GUI.value.invoke()

    # Application Window
    root = tk.Tk()
    root.title("Configure Sim")
    #root.geometry("1041x1210")
    root.iconify()

    # palette - currently hard coded
    palette = p.Drapion

    # main window
    Main = MainWindow(root, background = palette.Background.value)
    Main.pack(expand=True, fill='both')
    #======#
    # MENU #
    #======#

    """
    DIRECTORY VARIABLES
    
    Generally, the structure of this involves an observer class storing the main DIR's value.
    Subdirs are system.path.Path instances that contain an update() function to appropriately re-initialize
    its path attribute when the main DIR is updated.
    
    Make sure that widgets pass references to these variables.
    """

    # Selected dirs for sims
    DIR_Inputs = Data('DIR_INPUTS')
    DIR_Inputs.data = runtime_configs['Paths']["Inputs"]
    #print(DIR_Inputs.data)

        # Initial setters
    DIR_Particle = Path(os.path.join(DIR_Inputs.data, NAME_PARTICLES), NAME_PARTICLES)
    DIR_Coil = Path(os.path.join(DIR_Inputs.data, NAME_COILS), NAME_COILS)
    #DIR_coilDefs = os.path.join(DIR_Inputs, NAME_COILS)
    DIR_lastUsed = Path(os.path.join(DIR_Inputs.data, NAME_lastUsed), NAME_lastUsed)
    DIR_Bob = Path(os.path.join(DIR_Inputs.data, "bob_e"), "bob_e")

    DIR_Output = Path(os.path.join(DIR_ROOT, NAME_OUTPUTS), NAME_OUTPUTS) # output is not a subdir of Inputs so it's spared from the next step

        # Add to observer class so they update when DIR_Inputs is updated
    subdirs = [DIR_Particle, DIR_Coil, DIR_lastUsed, DIR_Bob]
    for subdir in subdirs:
        DIR_Inputs.attach(subdir)

    # PLOT OR CALCULATE?
    """
    MAIN TABS
    The 'plot' or 'calculate' tab on the top of the GUI window.
    """
    style1 = ttk.Style()
    style1.theme_use('default')
    style1.configure('Two.TNotebook.Tab', 
                    font=('Arial', 18),
                    padding=8,
                    borderwidth=0,
                    foreground='black',
                    background = palette.Text.value)

    style1.configure('Two.TNotebook', 
                    tabposition="n",
                    borderwidth=0, 
                    background='white')

    style1.map(
        'Two.TNotebook.Tab',
        background = [("selected", palette.Text_Bright.value)],
        foreground = [("selected", 'black')],
        font=[("selected", ('Arial', 18, 'bold'))]
    )

    tabControl=ttk.Notebook(Main, padding="0 12 2 0", style='Two.TNotebook')
    ## Create tab objects
    tab_calc = tk.Frame(tabControl, bg='gray')
    tab_plot = ttk.Frame(tabControl, padding="4 12 12 4")


    '''
    NESTED TABS:
    Here I will define a style for this, as I want these tabs to look different from the first ones.
    These tabs are for the coil and particle parameter options in the main calculate tab.
    '''

    style = ttk.Style()
    style.theme_use('default')
    style.configure('One.TNotebook.Tab', 
                    font=('Arial', 12), 
                    padding=(15, 10), 
                    justify="center", 
                    width=8,
                    borderwidth=0,
                    foreground='light gray',
                    background=palette.Background.value)

    style.configure('One.TNotebook', 
                    tabposition='wn', 
                    tabmargins=0,
                    borderwidth=0,
                    background = palette.Background.value)
    style.map(
        'One.TNotebook.Tab',
        background=[("selected", palette.Background.value)],
        foreground=[("selected", "white")],
        font=[("selected", ('Arial', 14, 'bold'))]
    )

    calc_nested_notebook = ttk.Notebook(tab_calc, style='One.TNotebook')

    calc_frame1 = tk.Frame(calc_nested_notebook, relief='flat', background="light gray")
    calc_frame1_scroll = ScrollableFrame(calc_frame1)

    #calc_frame3 = tk.Frame(calc_nested_notebook, background="light gray")
    #calc_frame3_scroll = ScrollableFrame(calc_frame3)

    calc_debug_frame = tk.Frame(calc_nested_notebook, relief='flat', background="light gray")

    #   PLACE THE NESTED NOTEBOOKS IN LABEL FRAMES SO THEY ARE NOT CONFUSING AF
    b_field_labelFrame = ttk.LabelFrame(calc_debug_frame, text="B-Field")
    e_field_labelFrame = ttk.LabelFrame(calc_debug_frame, text="E-Field")

    field_notebook = Field_Notebook(b_field_labelFrame, ['zero', 'magpy'],
                                    [ZeroTableTab, RingTableTab],
                                    collection_key=(param_keys.field_methods.name, 'b', param_keys.params.name, 'collection'),
                                    tab_key=(param_keys.field_methods.name, 'b', 'method'),
                                    dataclasses = [None, CircleCurrentConfig],
                                    dir_names=[None, "CoilConfigurations"],
                                    path_key='coil_file',
                                    field="b")
    field_notebook.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    e_field_notebook = Field_Notebook(e_field_labelFrame, ['zero', 'bob_e', 'fw_e', 'disk_e'],
                                      [ZeroTableTab, RingTableTab, RingTableTab, DiskTab],
                                    collection_key=(param_keys.field_methods.name, 'e', param_keys.params.name, 'collection'),
                                    tab_key=(param_keys.field_methods.name, 'e', 'method'),
                                    dataclasses= [None, Bob_e_Config_Dataclass, Bob_e_Config_Dataclass, Disk_e_Config_Dataclass],
                                    dir_names=[None, 'bob_e', 'bob_e', 'Disks'],
                                      path_key="e_coil_file",
                                      field="e")
    e_field_notebook.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    b_field_labelFrame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    e_field_labelFrame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

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

    plot_graph_traj = tk.Frame(plot_title_LFrame)
    plot_graph_traj.grid(row=1)


    ## WIDGETS
    ### Output Files
    label_out_file = ttk.Label(plot_out_file,
                                text = "Output File Dir:")
    label_out_file.grid(row = 0, column= 0, padx=10, pady=10)

    button_out_file = tk.Button(plot_out_file,
                                    text = "Browse Files")
    button_out_file.grid(row = 0, column=1, pady=10)

    name_out_file_var = tk.StringVar(value="No Output File Selected")
    name_out_file = ttk.Label(plot_out_file,
                            textvariable=name_out_file_var)
    name_out_file.grid(row = 0, column=2, pady=10)

    #################
    # GRAPH WINDOWS #
    #################

    trajectoryGraph = PlottingWindowObj(plot_graph_traj, Main, name_out_file_var)
    trajectoryGraph.grid(row=0, column=0)

    '''
    We need to keep watch on the selected data file value, and ensure that this button is active only when
    there is a valid data file selected.
    '''
    button_out_file.config(command=partial(PlotFileCallback, name_out_file_var, DIR_Output))

    #=============#
    # GUI WIDGETS #
    #=============#
    style = ttk.Style()
    style.configure("LG.TCheckbutton", background="light gray", foreground="black", indicatorbackground="black", indicatorforeground="white")

    # FRAMES
    ## MAIN CONTAINER
    calc_title_LFrame = ttk.Frame(calc_frame1_scroll.frame)
    calc_title_LFrame.columnconfigure(0, weight=1)

    ### SUB CONTAINERS
    CalcCheckBoxFrame = tk.Frame(calc_title_LFrame, bg="light gray")
    CalcCheckBoxFrame.grid(row=1, column=0, pady=10, padx=10, sticky="WSEW")

    CalcRestartFileFrame = tk.Frame(calc_title_LFrame)
    CalcRestartFileFrame.grid(row=2, column= 0, pady=10, padx=10)

    Particle = tk.LabelFrame(calc_frame1_scroll.frame, text="Particle Conditions")

    DropdownFrame = tk.Frame(Particle)
    DropdownFrame.grid(row=0, column=0, sticky="WSEW")

    ParticlePreviewFrame = tk.Frame(Particle)
    ParticlePreviewFrame.grid(row=1, column=0, sticky="WSEW")

    CalcTimeStepFrame = tk.LabelFrame(calc_title_LFrame, bg="light gray", text="Time, Step")
    CalcTimeStepFrame.grid(row=0, column=0, sticky="NSEW")

    '''
    FieldGraphs = tk.LabelFrame(calc_frame1_scroll.frame, bg="light gray", text="Fields")

    Fields = tk.LabelFrame(FieldGraphs, bg="light gray", text="Static Fields")
    Fields.grid(row=0, column=0, sticky="WSEW", padx=10, pady=10)

    Fields0 = tk.Frame(Fields)
    Fields0.grid(row=0, column=0, sticky="WSEW", padx=5, pady=5)
    Fields1 = tk.Frame(Fields)
    Fields1.grid(row=0, column=1, sticky="WSEW", padx=5, pady=5)

    EGraphFrame = tk.LabelFrame(FieldGraphs, bg="light gray", text="E-field")
    EGraphFrame.grid(row=1, column=0)

    EGraphFrame_for_Canvas = tk.Frame(EGraphFrame) # contains the canvas for the graph. done so that the elements above are placed independently.
    EGraphFrame_for_Canvas.grid(row=1, column=0)

    EGraphFrame_for_Buttons = tk.Frame(EGraphFrame)
    EGraphFrame_for_Buttons.grid(row=0, column=0)
    '''

    ## Particle condition stuff..
    #Combobox_particle_file = FileDropdown(DropdownFrame,
    #                                              dir=DIR_Particle)
    #Combobox_particle_file.grid(row=0, column=0)
    particlePreview = ParticlePreview(ParticlePreviewFrame, dir_observed=DIR_Particle)
    calc_frame1_scroll._add_Subscriber(particlePreview) # I do this so that I can run the table's update function when this tab becomes selected.
    
    ## FIELDS!!!!!!
    """
    b_field = FieldDropdown(Fields0,
                        fm.B_Methods,
                        "B-Field: ",
                        key=param_keys.b.name)
    b_field.grid(row=0, column=0)

    e_field= FieldDropdown(Fields0,
                        fm.E_Methods,
                        "E-Field: ",
                        key=param_keys.e.name)
    e_field.grid(row=1, column=0)
    """

    ## Timestep stuff..
    time_info = TimeStep_n_NumStep(CalcTimeStepFrame)
    calc_frame1_scroll._add_Subscriber(time_info)

    # Graphing options for the field parameter settings.
    #field_graphs = FieldDropdown(EGraphFrame_for_Buttons, fm.FieldGraph_Methods, "Show me: ")
    #field_graphs.grid(row=0, column=0)

    ## Caclulate button
    calc_button = tk.Button(tab_calc,
                            text="Calculate",
                            width=10,
                            height=2,
                            font=("None", 12))
    calc_button.pack(anchor='s', side=BOTTOM)

    #===========================================================================================#
    ########################
    # CURRENT MANIPULATION #
    ########################

    #CurrentFrame = tk.LabelFrame(calc_frame3_scroll.frame, text="Configure Current")
    #CurrentFrame.grid(row = 1, column=0, padx=10, pady=10)
    #GraphFrame = tk.LabelFrame(calc_frame3_scroll.frame, text="Graph")
    #GraphFrame.grid(row = 2, column=0, padx=10, pady=10)
    #coil_config = CurrentConfig(CurrentFrame, DIR_Coil, GraphFrame)
    #calc_frame3_scroll._add_Subscriber(coil_config) # Done so table's update function runs when this tab is active.

    ### FIELD GRAPHS
    """
    written below currents to ensure they are loaded in 
    """
    #B_field_graph = FieldCoord_n_Graph(b_field, BGraphFrame, coil_config.GraphB)
    """
    E_field_graph = FieldCoord_n_Graph(table = e_field,
                                       root=Main,
                                       graphOptions=field_graphs, 
                                    graphFrame= EGraphFrame_for_Buttons, 
                                    canvasFrame=EGraphFrame_for_Canvas,
                                    currentTable=coil_config.table,
                                    title="E on X-Z Plane",
                                    x_label="X (m)",
                                    y_label="Y (A)")
    """
    #=======#
    # FINAL #
    #=======#
    #PACKING
    tab_calc.pack(fill='both', expand=True)
    tabControl.add(tab_calc, text="Calculate", padding=(5,5))
    tabControl.add(tab_plot,text="Plot", padding=(5,5))
    tabControl.pack(expand=1, fill="both", side=TOP)

    calc_frame1.pack(side="top", fill="both", expand=True)
    #calc_frame3.pack(side="top", fill="both", expand=True)
    calc_frame1_scroll._InternalPack()
    #calc_frame3_scroll._InternalPack()
    Main.scrollables.append(calc_frame1_scroll)
    #Main.scrollables.append(calc_frame3_scroll)


    calc_title_LFrame.pack(fill="x", side="top", expand=True)
    Particle.pack(fill="x", side="top", expand=True)
    #FieldGraphs.pack(fill="x", side="top", expand=True)


    calc_nested_notebook.add(calc_frame1, text="Particle")

    #calc_nested_notebook.add(calc_frame3, text="Coils")
    calc_nested_notebook.add(calc_debug_frame, text="Fields")
    calc_nested_notebook.pack(expand=True, fill='both', side=LEFT)
    
    """
    REGISTER SCROLLING FRAME AREAS
    """
    root.update()
    calc_frame1_scroll.RegisterScrollArea()
    #calc_frame3_scroll.RegisterScrollArea()


    """
    LOGIC FOR PASSING PARAMS BACK TO THE PROGRAM.
    """
    subs = {}

    # control what classes to send over to the program by adding it to params
    #subs["params"] = [time_info, particlePreview, coil_config, b_field, e_field, E_field_graph]
    subs["params"] = [time_info, particlePreview]
    Events.INIT_GUI.value.invoke(widgets=subs['params'])
    root.deiconify()

    calc_button.configure(command=partial(open_output_config, subs["params"], DIR_lastUsed.path.data, root, manager)) # update calculate button's command after setting up params
    FillWidgets(subs["params"], DIR_lastUsed)

    """
    REGISTER EVENT FUNCTIONS
    """
    # Refresh tables when switching between param and coil tabs
    # Reminds the program to switch classes when dealing with their class functions.
    #calc_nested_notebook.bind('<<NotebookTabChanged>>', OnNotebookTabChanged)
    tabControl.bind('<<NotebookTabChanged>>', lambda event, i=trajectoryGraph: on_main_notebook_tab_changed(event, i))

    def on_close():
        Events.ON_CLOSE.value.invoke()
        root.quit()
        root.destroy()
        manager.shutdown()
    root.protocol("WM_DELETE_WINDOW", on_close)

    #calc_nested_notebook.event_generate("<<NotebookTabChanged>>") # really really really make sure that the active tab's elements are refreshed on start.
    root.mainloop()

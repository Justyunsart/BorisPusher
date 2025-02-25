from tkinter import ttk
import tkinter as tk
from GuiHelpers import *
from functools import partial
from CurrentGuiClasses import *
from BorisGuiClasses import *
import palettes as p
from ScrollableFrame import ScrollableFrame
#######
# GUI #
#######
def OpenGUI():
    '''
    Testing the code by changing parameters and numsteps and everything became too cumbersone, so I decided to
    bite the bullet and create some GUI for it. 

    This is the main hub for the GUI, with many helper files providing classes and functions.
    '''

    # Application Window
    root = tk.Tk()
    root.title("Configure Sim")
    root.geometry("1000x1500")

    # palette - currently hard coded
    palette = p.Drapion

    # main window
    Main = MainWindow(root, background = palette.Background.value)
    Main.pack(expand=True, fill='both')
    #Main.grid_rowconfigure(0, weight=1)
    #Main.grid_columnconfigure(0, weight=1)

    #======#
    # MENU #
    #======#

    # add the toolbar
    mainToolbar = ConfigMenuBar(Main)

    """
    KEY VARS
    """
    # Selected dirs for sims
    Main_PrefFiles = Main.prefs
    DIR_Particle = Main_PrefFiles.DIR_particle
    DIR_Coil = Main_PrefFiles.DIR_coil
    DIR_coilDefs = Main_PrefFiles.DIR_coilDefs
    DIR_lastUsed = Main_PrefFiles.DIR_lastUsed

    #print(DIR_Particle)

    # PLOT OR CALCULATE?
    """
    MAIN TABS
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
    #tabControl.grid(row=0, column=0, sticky=N+W+E+S)

    ## Create tab objects
    tab_calc = tk.Frame(tabControl, bg='gray')

    #tab_calc.grid_columnconfigure(0, weight = 1)
    #tab_calc.grid_rowconfigure(0, weight = 1)

    tab_plot = ttk.Frame(tabControl, padding="4 12 12 4")
    #tab_plot.grid_columnconfigure(0, weight = 1)
    #tab_plot.grid_rowconfigure(0, weight = 1)


    #tabControl.grid_rowconfigure(0, weight=1)
    #tabControl.grid_columnconfigure(0, weight=1)


    '''
    NESTED TABS:
    Here I will define a style for this, as I want these tabs to look different from the first ones.
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

    # Scroll wheel for tabs
    #calc_frame1_scrollwheel = tk.Scrollbar(calc_frame1, orient="vertical")
    #calc_frame1_scrollwheel.grid(row=0, column=9, sticky="NE")
    #calc_frame1.grid_columnconfigure(9, weight=1)

    #calc_frame2 = ttk.Frame(calc_nested_notebook, width=200, height=100, relief=tk.SUNKEN)
    calc_frame3 = tk.Frame(calc_nested_notebook, background="light gray")

    calc_frame3_scroll = ScrollableFrame(calc_frame3)

    #calc_nested_notebook.grid(row=0, column=0, sticky="nw")
    #calc_nexted_label_frame = tk.Frame(tab_calc)

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
                                text = "Output File Dir:")#.grid(column = 0, row = 1, sticky=(W))
    label_out_file.grid(row = 0, column= 0, padx=10, pady=10)

    button_out_file = tk.Button(plot_out_file,
                                    text = "Browse Files")
    button_out_file.grid(row = 0, column=1, pady=10)

    name_out_file = ttk.Label(plot_out_file,
                            text="No Output File Selected")
    name_out_file.grid(row = 0, column=2, pady=10)

    #################
    # GRAPH WINDOWS #
    #################
    from PlottingWindow import TrajGraph

    trajectoryGraph = TrajGraph(plot_graph_traj)


    #button_out_file.config(command=partial(browseFiles, name_out_file))

    ### Confirm Button
    '''
    We need to keep watch on the selected data file value, and ensure that this button is active only when
    there is a valid data file selected.
    '''
    plot_confirm = tk.Button(tab_plot,
                            text="Create Plot",
                            state="disabled")
    button_out_file.config(command=partial(PlotFileCallback, name_out_file, plot_confirm))
    plot_confirm.config(command=partial(trajectoryGraph.UpdateGraph, name_out_file))


    plot_confirm.grid(sticky=S)



    # CALCULATION GUI#

    #=============#
    # GUI WIDGETS #
    #=============#

    style = ttk.Style()
    style.configure("LG.TCheckbutton", background="light gray", foreground="black", indicatorbackground="black", indicatorforeground="white")

    # FRAMES


    ## MAIN CONTAINER
    calc_title_LFrame = ttk.Frame(calc_frame1_scroll.frame)
    calc_title_LFrame.columnconfigure(0, weight=1)
    #calc_title_LFrame.grid(row=0, column=0, pady=10, padx=10, sticky="NW")

    ### SUB CONTAINERS


    CalcCheckBoxFrame = tk.Frame(calc_title_LFrame, bg="light gray")
    CalcCheckBoxFrame.grid(row=1, column=0, pady=10, padx=10, sticky="WSEW")

    CalcRestartFileFrame = tk.Frame(calc_title_LFrame)
    CalcRestartFileFrame.grid(row=2, column= 0, pady=10, padx=10)

    Particle = tk.LabelFrame(calc_frame1_scroll.frame, text="Particle Conditions")
    #Particle.grid(row=1, column=0, sticky="E")

    DropdownFrame = tk.Frame(Particle)
    DropdownFrame.grid(row=0, column=0, sticky="WSEW")

    ParticlePreviewFrame = tk.Frame(Particle)
    ParticlePreviewFrame.grid(row=1, column=0, sticky="WSEW")

    CalcTimeStepFrame = tk.LabelFrame(calc_title_LFrame, bg="light gray", text="Time, Step")
    CalcTimeStepFrame.grid(row=0, column=0, sticky="NSEW")


    FieldGraphs = tk.LabelFrame(calc_frame1_scroll.frame, bg="light gray", text="Fields")
    #FieldGraphs.grid(row=0, column=1)

    Fields = tk.LabelFrame(FieldGraphs, bg="light gray", text="Static Fields")
    Fields.grid(row=0, column=0, sticky="WSEW", padx=10, pady=10)

    #BGraphFrame = tk.LabelFrame(FieldGraphs, bg="light gray", text="B-field")
    #BGraphFrame.grid(row=0, column=0)

    EGraphFrame = tk.LabelFrame(FieldGraphs, bg="light gray", text="E-field")
    EGraphFrame.grid(row=1, column=0)


    ## Particle condition stuff..
    Combobox_particle_file = Particle_File_Dropdown(DropdownFrame,
                                                    dir=DIR_Particle)
    #particleCheckboxes = ParticlePreviewSettings(DropdownFrame)
    particlePreview = ParticlePreview(ParticlePreviewFrame,
                                    Combobox_particle_file)
    calc_frame1_scroll._add_Subscriber(particlePreview) # I do this so that I can run the table's update function when this tab becomes selected.
    ## FIELDS!!!!!!
    import FieldMethods as fm
    #b_field = CoordTable(Fields, title="B-Field")
    b_field = FieldDropdown(Fields,
                        fm.B_Methods,
                        "B-Field: ",
                        default=1)
    b_field.grid(row=0, column=0)

    #e_field = E_CoordTable(Fields, title="E-Field")
    e_field= FieldDropdown(Fields,
                        fm.E_Methods,
                        "E-Field: ")
    e_field.grid(row=1, column=0)

    ## Caclulate button
    calc_button = tk.Button(tab_calc,
                            text="Calculate",
                            width=10,
                            height=2,
                            font=("None", 12))
    calc_button.pack(anchor='s', side=BOTTOM)

    '''
    calc_nexted_label_frame.pack(side=TOP, anchor= NW, fill=Y)
    submenu = tk.Label(calc_nexted_label_frame, text="Submenus", 
                    foreground='white', 
                    padx=15, pady=5,
                    background=palette.Background.value, 
                    width=10,
                    font=("Arial", 12, "underline"),
                    justify="center"
                    ).pack(side=LEFT)
    '''



    #===========================================================================================#
    ########################
    # CURRENT MANIPULATION #
    ########################

    CurrentFrame = tk.LabelFrame(calc_frame3_scroll.frame, text="Configure Current")
    CurrentFrame.grid(row = 1, column=0, padx=10, pady=10)
    GraphFrame = tk.LabelFrame(calc_frame3_scroll.frame, text="Graph")
    GraphFrame.grid(row = 2, column=0, padx=10, pady=10)
    coil_config = CurrentConfig(CurrentFrame, DIR_Coil, DIR_coilDefs, GraphFrame)
    calc_frame3_scroll._add_Subscriber(coil_config) # Done so table's update function runs when this tab is active.

    ### FIELD GRAPHS
    """
    written below currents to ensure they are loaded in 
    """
    #B_field_graph = FieldCoord_n_Graph(b_field, BGraphFrame, coil_config.GraphB)
    E_field_graph = FieldCoord_n_Graph(table = e_field, 
                                    graphFrame= EGraphFrame, 
                                    currentTable=coil_config.table,
                                    title="E on X-Z Plane",
                                    x_label="X (m)",
                                    y_label="Y (A)")

    ## Timestep stuff..
    time_info = TimeStep_n_NumStep(CalcTimeStepFrame, coil_config.table)

    """
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
    calc_frame3.pack(side="top", fill="both", expand=True)
    calc_frame1_scroll._InternalPack()
    calc_frame3_scroll._InternalPack()


    calc_title_LFrame.pack(fill="x", side="top", expand=True)
    Particle.pack(fill="x", side="top", expand=True)
    FieldGraphs.pack(fill="x", side="top", expand=True)


    calc_nested_notebook.add(calc_frame1, text="Particle")
    #calc_nested_notebook.add(calc_frame2, text="Particle")

    calc_nested_notebook.add(calc_frame3, text="Coil")
    calc_nested_notebook.pack(expand=True, fill='both', side=LEFT)
    
    """
    REGISTER SCROLLING FRAME AREAS
    """
    root.update()
    calc_frame1_scroll.RegisterScrollArea()
    calc_frame3_scroll.RegisterScrollArea()

    """
    REGISTER EVENT FUNCTIONS
    """
    # Refresh tables when switching between param and coil tabs
    # Reminds the program to switch classes when dealing with their class functions.
    calc_nested_notebook.bind('<<NotebookTabChanged>>', OnNotebookTabChanged)
    
    """
    LOGIC FOR PASSING PARAMS BACK TO THE PROGRAM.
    """
    subs = {}

    # control what classes to send over to the program by adding it to params
    subs["params"] = [time_info, particlePreview, coil_config, b_field, E_field_graph]

    calc_button.configure(command=partial(CalculateCallback, subs["params"], DIR_lastUsed)) # update calculate button's command after setting up params
    FillWidgets(subs["params"], DIR_lastUsed)

    def on_close():
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    print("exited")

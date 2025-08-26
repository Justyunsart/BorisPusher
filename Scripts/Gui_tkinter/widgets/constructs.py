import tkinter as tk
from tkinter import ttk
from Gui_tkinter.widgets.ScrollableFrame import ScrollableFrame
from system.state_dict_main import AppConfig

"""
Widget creation without having to subclass; useful for one-offs.
"""

def build_main_notebook(parent):
    """
    The notebook holds the 'calc' and 'plot' tabs
    """
    tabControl = ttk.Notebook(parent, padding="0 12 2 0", style='Two.TNotebook')

    tab_calc = tk.Frame(tabControl, bg='gray')
    tab_plot = ttk.Frame(tabControl, padding="4 12 12 4")

    # add a button to confirm the calculation
    calc_button = tk.Button(tab_calc,
                            text="Calculate",
                            width=10,
                            height=2,
                            font=("None", 12))
    calc_button.pack(anchor='s', side=BOTTOM)

    return tabControl, tab_calc, tab_plot, calc_button

def build_calc_notebook(parent):
    """
    The notebook holds the submenus for parameters (params, fields, visuals)
    """
    calc_nested_notebook = ttk.Notebook(parent, style='One.TNotebook')

    param_frame = tk.Frame(calc_nested_notebook, relief='flat', background="light gray")
    field_frame = tk.Frame(calc_nested_notebook, relief='flat', background="light gray")
    field_frame.pack(fill='both', expand=True)
    field_frame_s = ScrollableFrame(field_frame)
    vis_frame = tk.Frame(calc_nested_notebook, relief='flat', background="light gray")

    return calc_nested_notebook, param_frame, field_frame, vis_frame, field_frame_s

from system.temp_file_names import param_keys
from Gui_tkinter.widgets.notebook.widget import Field_Notebook
from Gui_tkinter.widgets.notebook.tab_content import *
from Gui_tkinter.funcs.GuiEntryHelpers import *
from system.state_dict import *

def build_field_tab(parent, params:AppConfig):
    """
    The field tab contains notebooks for the currently selected field.
    There are two of these (for B and E fields)
    """

    #   PLACE THE NESTED NOTEBOOKS IN LABEL FRAMES SO THEY ARE NOT CONFUSING AF
    b_field_labelFrame = ttk.LabelFrame(parent.frame, text="B-Field")
    e_field_labelFrame = ttk.LabelFrame(parent.frame, text="E-Field")

    field_notebook = Field_Notebook(b_field_labelFrame, ['zero', 'magpy'],
                                    [ZeroTableTab, RingTableTab],
                                    collection_key="b.collection",
                                    tab_key="b.method",
                                    dataclasses=[None, CircleCurrentConfig],
                                    param_classes=[None, FieldConfig],
                                    dir_names=[None, "CoilConfigurations"],
                                    path_key="path.b",
                                    name_key='b.name',
                                    field="b",
                                    params=params)
    field_notebook.pack(fill='both', expand=True)

    e_field_notebook = Field_Notebook(e_field_labelFrame,
                                      ['zero', 'bob_e', 'disk_e', 'washer_potential'],
                                      [ZeroTableTab, RingTableTab, DiskTab, DiskTab],
                                      collection_key='e.collection',
                                      tab_key='e.method',
                                      dataclasses=[None, Bob_e_Config_Dataclass,
                                                   Disk_e_Config_Dataclass, Disk_e_Config_Dataclass],
                                      param_classes=[None, ResFieldConfig,
                                                     WasherFieldConfig, WasherFieldConfig],
                                      dir_names=[None, 'bob_e', 'bob_e', 'Disks', "Disks"],
                                      path_key="path.e",
                                      name_key="e.name",
                                      field="e",
                                      params=params)
    e_field_notebook.pack(fill='x', expand=True)

    # order of field notebooks
    b_field_labelFrame.pack(fill='x', expand=True)
    e_field_labelFrame.pack(fill='x', expand=True)


    return b_field_labelFrame, e_field_labelFrame #only return parent frame b/c it already stores its children

from Gui_tkinter.widgets.dt_np import TimeStep_n_NumStep
from Gui_tkinter.funcs.GuiHelpers import *
from Gui_tkinter.widgets.BorisGuiClasses import *

def build_params_tab(parent, DIR_Particle, params:AppConfig):
    """
    the params tab holds high level stuff like dt/numsteps, particle information
    """
    # I made the widget classes here not as tk.Frame subclasses, so we have to first make the frame
    CalcTimeStepFrame = tk.LabelFrame(parent, bg="light gray", text="Time, Step")
    ParticlePreviewFrame = tk.Frame(parent)

    # Actual widget creation
    time_info = TimeStep_n_NumStep(parent, params)
    particlePreview = ParticlePreview(ParticlePreviewFrame, dir_observed=DIR_Particle, params=params)

    # Packing
    CalcTimeStepFrame.grid(row=0, column=0, sticky="NSEW")
    ParticlePreviewFrame.grid(row=1, column=0, sticky="WSEW")

    return time_info, particlePreview

from Gui_tkinter.widgets.PlottingWindow import PlottingWindowObj
def build_plot_tab(parent, main, DIR_Output, params):
    """
    the plotting tab is simpler because everything is on one page.
    It's where we open plotfiles to visualize them.
    """
    plot_title_LFrame = ttk.LabelFrame(parent,
                                       text="Plotting")
    plot_title_LFrame.grid(row=0, sticky="NWES", padx=10, pady=10)

    plot_out_file = ttk.LabelFrame(plot_title_LFrame,
                                   text="Data Source")
    plot_out_file.grid(row=0, padx=10, pady=10)

    plot_graph_traj = tk.Frame(plot_title_LFrame)
    plot_graph_traj.grid(row=1)

    ## WIDGETS
    ### Output Files
    label_out_file = ttk.Label(plot_out_file,
                               text="Output File Dir:")
    label_out_file.grid(row=0, column=0, padx=10, pady=10)

    button_out_file = tk.Button(plot_out_file,
                                text="Browse Files")
    button_out_file.grid(row=0, column=1, pady=10)

    name_out_file_var = tk.StringVar(value="No Output File Selected")
    name_out_file = ttk.Label(plot_out_file,
                              textvariable=name_out_file_var)
    name_out_file.grid(row=0, column=2, pady=10)

    #################
    # GRAPH WINDOWS #
    #################

    trajectoryGraph = PlottingWindowObj(plot_graph_traj, main, name_out_file_var)
    trajectoryGraph.grid(row=0, column=0)

    '''
    We need to keep watch on the selected data file value, and ensure that this button is active only when
    there is a valid data file selected.
    '''
    button_out_file.config(command=partial(PlotFileCallback, name_out_file_var, DIR_Output))

from Gui_tkinter.widgets.field_graph import GraphFactory, FieldDropdownFigure
from Gui_tkinter.widgets.base import ParamWidget
from EFieldFJW.e_solvers import *
from EFieldFJW.e_graphs import *

def build_field_vis_tab(parent, params:AppConfig):
    """
    This tab will include a dropdown menu for selecting options
    coupled with a canvas that will be filled with the selected graphical visualization.
    """
    def update_graph(*args, **kwargs):
        """
        callback whenever the graphing button is pressed.
            1. Read the currently selected dropdown option
            2. Get the appropriate function call, field w/ graph_option value
            3. With the field of interest from (2), query params for the currently active field method
                > params.{field}.method
            4. With the method from (3), get the respective GraphFactory instance from the field's graph_registry dict.
            5. Tell that GraphFactory instance to make a Grapher instance
            6. Tell that Grapher instance to run the unbounded function from (2)
        """
        # 1-2: Get graph_option value by key (name of selected option)
        current_option = widget.selected_option.get() #key of graph_options
        unbound_func, cur_field = graph_options.get(current_option) #(func, field)

        # 3: Get the appropriate field's method name from
        current_method = ParamWidget.get_nested_field(params, f"{cur_field}.method") #'{e/b}.
        # 4: Get the current GraphFactory instance
        current_factory = graph_registry.get(current_method)
        # 5: Tell that factory instance to make its Grapher instance
        kwargs = make_args.get(current_method)
        if kwargs is not None:
            grapher = current_factory.make(**kwargs)
        else:
            grapher = current_factory.make()
        # 6: Tell that grapher to run the unbounded function.
        widget.reset_graph() #clear graph first
        bound_func = unbound_func.__get__(grapher, grapher.__class__)
        bound_func(instance=widget, method=current_method)
        widget.canvas_widget.draw()

    # METADATA #
    ############
    # We can see here the graphical options that exist, as well as the functions called for each option.
    # Available dropdown menu options
    graph_options = {
        "E Contour" : (Grapher.graph_contour, "e"),
        "E Streamplot" : (Grapher.graph_streamline, "e"),
        "B Contour" : (Grapher.graph_contour, "b"),
        "B Streamplot" :(Grapher.graph_streamline, "b"),
    }

    # Solver and Grapher pairings for each field solver method.
    # TODO: ADD THE REST OF THE E OPTIONS
    graph_registry = {
        "bob_e": GraphFactory(Bob_e_Solver, Bob_e_Grapher, field='e', params=params),
        "washer_potential" : GraphFactory(Washer_Potential_e_Solver, Washer_Potential_e_Grapher, field='e', params=params),
        "disk_e" : GraphFactory(Disk_e_Solver, Disk_e_Grapher, field='e', params=params),
        'magpy' : GraphFactory(MagpySolver, MagpyGrapher, field='b', params=params)
        # "disk_e": GraphFactory(Bob_e_Solver, Bob_e_Grapher, **graph_args, collection=params.e.collection),
    }
    # extra keyword arguments to call when creating the grapher instance.
    make_args = {
        "washer_potential" : {'inners' : 'e.inner_r'},
        "disk_e": {'inners': 'e.inner_r'}
    }


    # CREATE WIDGET #
    #################
    widget = FieldDropdownFigure(parent, graph_options)
    widget.pack(expand=1, fill="both", side='top')

    # EVENT REGISTER #
    ##################
    widget.button.config(command=update_graph)

    return widget


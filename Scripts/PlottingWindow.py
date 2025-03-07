"""
Junk for integrating plotting visuals into the GUI window
"""
import magpylib as mp
from magpylib.current import Circle
from pathlib import Path
import os
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from GuiEntryHelpers import (JSON_to_Df, tryEval)
import pandas as pd
from GuiHelpers import CSV_to_Df
from BorisAnalysis import *

"""
the following r settings and callables that the classes will implement.
"""

# DEFAULT GRAPH SETTINGS:
graph_default = {
            "projection" : 'rectilinear',
            "title" : "New Graph",
            "xlab" : 'X (m)',
            "ylab" : "Y (m)",
            'zlab' : 'Z (m)'
}

# GRAPH STYLES: HOW TO SET UP EACH TYPE OF GRAPH (labels and stuff)
# defined only where they stray from the default settings.
"""
Reminder: the actual, complete style dict is stored as the graph_settings property in a CanvasFigure object.
It's done like this so I don't have to type literally everything.
"""
trajectory_style = {
    "projection" : '3d',
    'title' : 'Trajectory'
}

vel_step_style = {
    'title' : 'Vel vs. Step',
    'ylab' : 'm/s'
}

b_step_style = {
    'title' : 'B-mag vs. Step',
    'ylab' : 'T'
}

e_step_style = {
    'title' : 'E-mag vs. Step'
}

# available graphing options. Stored in a ttk.combobx.
graph_options = ('Vel vs. Step',
                 'B-mag vs. Step',
                 'E-mag vs. Step')

# GRAPHING FUNCTIONS - each option should be accompanied by a function.
"""
These functions expect a pre-labelled, empty subplot to draw on.
Also, they do not call the draw function. That should be done externally.

Pls note that right now, they will only graph the data of particle 0.
"""
def Param_v_Step_callable(fig, plot, df:pd.DataFrame, id, **kwargs):
    """
    for tracking a single parameter involved in the simulation as a linegraph respective to the step count.
    used for the vel, b-mag, e-mag v, step graphs.
    """
    xn = None
    yn = None # these are strings that will be populated with the appropriate df col names.
    zn = None
    
    # the id parameter lets this function know what to look for in the dataframe.
    match id:
        case 'v':
            xn = 'vx'
            yn = 'vy'
            zn = 'vz'
        case 'b':
            xn = 'bx'
            yn = 'by'
            zn = 'bz'
        case 'e':
            xn = 'ex'
            yn = 'ey'
            zn = 'ez'
        case _:
            print(f"YOU PROVIDED AN UNSUPPORTED ID TO PlottingWindow.Param_v_Step_callable!! {id} is not v, b, nor e!")

    # now that we know the column names associated with the data we want, we index the dataframe with the relevant info
    dfslice = df[df['id'] == 0] # right now, we only look at the 1st particle.
    x, y, z = dfslice[xn].to_numpy(), dfslice[yn].to_numpy(), dfslice[zn].to_numpy() #x, y, z coord points at each step
    coords = np.column_stack((x,y,z))

    # get the graphable components
    # 1. the magnitude of the component at each step.
    step_mag = magnitude_at_each_step(coords)

    # for now, b has only this line.
    if id == 'b':
        plot.plot(step_mag)
        return True
    else:
        # everyone else gets parallel and perpendicular components also graphed, which are calculated relative to b.
        bx,by,bz = dfslice["bx"].to_numpy(), dfslice["by"].to_numpy(), dfslice["bz"].to_numpy() # b components at each step to calculate v||, e||
        bs = np.column_stack((bx, by, bz)) # b coordinates all in one array.

        # get the parallel and perpendicular components relative to b
        step_parallel = get_parallel(bs, coords)
        step_perpendicular = get_perpendicular(bs, coords)

        # graph these guys.
        plot.plot(step_mag, label='magnitude', color='green')
        plot.plot(step_parallel, label='parallel', color='blue')
        plot.plot(step_perpendicular, label='perpendicular', color='red')


def Trajectory_callable(fig, plot, df:pd.DataFrame, c:mp.Collection, **kwargs):
    """
    for graphing the 3d trajectory of a single particle.
    """
    palettes = ["copper", "gist_heat"] # supported palettes for multiple particles.
    # get the number of particles. Because 'id' is working with a 0 index, add 1.
    nump = df["id"].max() + 1
    
    # Graph trajectory for each particle
    for part in range(nump):
        # extract data from dataframe
        dfslice = df[df["id"] == part] # only using info from the corresponding particle id.
        x, y, z = dfslice["px"].to_numpy(), dfslice["py"].to_numpy(), dfslice["pz"].to_numpy() #x, y, z coord points at each step
        
        # make the matching index's color palette a colormap distributed across the steps.
        colors = mpl.colormaps[palettes[part]]
        
        # actually plot everything.
        plot.scatter(x,y,z, cmap=colors, c=np.linspace(0,1,len(x)), s=2.5)

    # Additionally, we want to also show the coil configuration.
    mp.show(c, canvas=plot)
    plot.get_legend().remove()



# option, style mapping, so the program knows what style goes with each option:
graph_option_style_map = {'Vel vs. Step' : {'id' : 'v', 'style': vel_step_style},
                          'B-mag vs. Step' : {'id' : 'b', 'style' : b_step_style},
                          'E-mag vs. Step': {'id' : 'e', 'style' : e_step_style}}

'''
the following r the actual classes that implement the previously established settings and functions.
'''
# CLASS
class CanvasFigure(tk.Frame):
    """
    A class that contains a matplotlib figure inside of itself, navigable with tkinter.
    """

    def __init__(self, master, **kwargs):
        # default settings for the figure displayed by the canvas.
        # used unless overwritten by kwargs.
        self.graph_settings = graph_default.copy()

        self.master = master
        # Overwrite any non-default settings.
        # Remove graph_settings relevant keywords in case we want to pass any kwargs to tk.Frame
        for key in self.graph_settings.keys():
            if key in kwargs.keys():
                self.graph_settings[key] = kwargs.pop(key)
        # Run init of tk.Frame
        super().__init__(master, **kwargs)
        self.config(highlightbackground='red', highlightthickness='1') # visualize frame bounds
        # Instantiate figure
        self.initFig()
        # After instantiating the figure, it can be placed in a tk.Canvas
        self.canvas = tk.Canvas(master=self)
        self.canvas.pack(side=tk.TOP, expand=1)
        self.graph = FigureCanvasTkAgg(self.fig, self.canvas)
        self.graph.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH)

    
    def initFig(self):
        """
        Instantiates a figure and subplot according to current settings.
        """
        self.fig = plt.figure()
        projection = self.graph_settings['projection']
        #print(projection)
        self.plot = self.fig.add_subplot(1,1,1, projection=projection)
        # apply labels outlined in graph settings.
        self.renameLabels()
        # initialize with tight layout so axes labels don't get cut off.
        self.fig.tight_layout()

    def renameLabels(self):
        """
        Selects titles and labels from graph_settings and applies it to the figure.
        """
        if self.plot is not None:
            # load settings
            title = self.graph_settings['title']
            xlab = self.graph_settings['xlab']
            ylab = self.graph_settings['ylab']
            # apply settings
            self.plot.set_title(title)
            self.plot.set_xlabel(xlab)
            self.plot.set_ylabel(ylab)
            # things to do if there is a 3d projection 
            if self.graph_settings['projection'] == '3d':
                self.plot.set_zlabel(self.graph_settings['zlab'])

    def prepareGraph(self):
        """
        To graph on this plot again, you must clear the graph and reapply labels.
        """
        # clear the plot of its impurities
        self.plot.cla()
        # replot the labels according to the settings.
        self.renameLabels()

    def updateGraph(self, df:pd.DataFrame, func:callable, **kwargs):
        """
        When called, the selected graphing logic will be called once more.

        It is expected that the dataframe is externally provided upon the function call.
        """
        self.prepareGraph()
        func(self.fig, self.plot, df, **kwargs) # the graphing logic is being applied here.
        self.fig.tight_layout()
        self.graph.draw()
        return True

class DropdownFigure(tk.Frame):
    """
    A FRAME THAT WILL CONTAIN A COMBOBOX.
    THIS COMBOBOX WILL HAVE VARIOUS GRAPHING OPTIONS TO CHOOSE FROM,
    WHICH WILL AUTOMATICALLY UPDATE THE INCLUDED GRAPH.
    """
    def __init__(self, master, **kwargs):
        self.master = master
        super().__init__(master, **kwargs)
        # store references to children
        self.canvFig = CanvasFigure(master=self, **kwargs)
        # elevating some CanvasFigure properties so I can access it as a DropdownFigure easily.
        self.canvas = self.canvFig.canvas
        self.graph = self.canvFig.graph
        self.fig = self.canvFig.fig
        self.plot = self.canvFig.plot
        self.settings = self.canvFig.graph_settings
        
        # properties for handling comboboxes. 
        self.chosenVal = tk.StringVar() # keep the chosen combobox option here so I can moderate changes.
        self.dropdown = ttk.Combobox(self, textvariable=self.chosenVal, state='readonly')
        # set options to the tuple defined at the top of the document
        self.dropdown['values'] = graph_options

        # Its widgets (dropdown mainly) will take up the top line, then the rest of the space
        # is for the canvas figure object
        self.dropdown.pack(expand=1, fill="x", side=tk.TOP)
        self.canvFig.pack(expand=1, fill=tk.BOTH, side=tk.TOP)

        # bind the combobox to appropriate events, like updating the internal style dictionary
        #self.dropdown.bind("<<ComboboxSelected>>", self.update_graph_settings)
    
    def external_bind(self, external_class):
        """
        when called, the external class will be bound to this object's combobox selected event
        with the function update_dropdown.

        I did this to make sure the combobox selected event could still retain a reference to the
        class instance that triggered it. (and update_graph_settings requires external class info for the dataframe).
        """
        self.dropdown.bind("<<ComboboxSelected>>", lambda event, i=self: external_class.update_dropdown(event, i))
    
    def update_graph_settings(self, event):
        """
        Whenever a new graph setting is chosen (a new value for the dropdown), the internal style dictionary gets 
        updated accordingly.

        Reminder: the style to option map is set at the top of this document.
        """
        # load the new dictionary
        new_dict = graph_option_style_map[self.chosenVal.get()]['style']
        # update the current dictionary with this one.
        self.settings = self.settings.update(new_dict)
        print(self.settings)
    
    def updateGraph(self, df:pd.DataFrame, **kwargs):
        """
        calls the updateGraph function (with identical parameters) to the CanvasFigure object.
        """
        try:
            # get the id: a value associated with the currently selected dropdown menu option.
            id = graph_option_style_map[self.chosenVal.get()]['id']

            # only do graphing stuff if id is not none; if something is acutally chosen lol.
            if id is not None:
                #print("you should be updating a dropdown graph.")
                self.canvFig.updateGraph(df, Param_v_Step_callable, id=id)
        except:
            return False

class PlottingWindowObj(tk.Frame):
    """
    A high level class that contains the layout of the plotting window.

    Event handling done internally to ensure window resizing doesn't mess up graphs.
    
    Calls to update graph done as follows:
        - the trajectory graph is updated from an external function call (in BorisGui), when a dataset file is selected.
        - the two programmable graphs are updated when a dropdown value is chosen, AND when there is a valid dataset file selected.
    
    This is accomplished by having the external event update the internal property 'df', which is a dataframe that is read from the .json dataset file.
    This internal property, after being updated, will have the program run its graphing function, in which the trajectory graph is updated according to the dataset.
    The two programmable graphs will check their corresponding dropdown box for the graphing logic to apply.
    """
    
    def __init__(self, master, root, label:tk.StringVar):
        # these settings are in pixels.
        self.padx = 5
        self.pady = 0

        self.root = root # a reference to the program's main window is necessary to get the window size.
        self.master = master
        self.df = None # the dataset read from the .json output file.
        self.c = None # the magpylib.collection object that was used to run the simulation.
        self.path = label
        super().__init__(master)
        self.config(highlightbackground='black', highlightthickness='2') # visualize frame bounds

        # we want a 3-plot structure with the trajectory plot dominating a whole column to itself.
        # Create figures.
        self.trajectory = CanvasFigure(master=self, projection='3d', title='Trajectory')
        self.graph1 = DropdownFigure(self)
        self.graph2 = DropdownFigure(self)

        # also for dropdown figures, we need to subscribe to their combobox changed events.
        # REMINDER: THIS IS SO THAT WE CAN PASS THE DATAFRAME PROPERTY FROM THIS CLASS TO THE DROPDOWNS WHILE TRIGGERING UPDATES FROM TK EVENTS.
        # update_dropdown from this class runs because of this.
        self.graph1.external_bind(self)
        self.graph2.external_bind(self)

        # Store figures and the canvases they live on.
        self.figs = [self.trajectory.fig, self.graph1.fig, self.graph2.fig] # the mpl fig object
        self.graphs = [self.trajectory.graph, self.graph1.graph, self.graph2.graph] # the FigureCanvasTkAgg objects
        self.plots = [self.trajectory.plot, self.graph1.plot, self.graph2.plot] # the subplots in the mpl figs
        self.canvases = [self.trajectory.canvas, self.graph1.canvas, self.graph2.canvas] # the canvases that hold the FigureCanvasTkAggs

        # packing step
        self.trajectory.pack(expand=1, side=tk.LEFT, anchor="w")
        self.graph1.pack(side=tk.TOP, anchor='ne', expand=1)
        self.graph2.pack(side=tk.TOP, anchor='se', expand=1)

        # event bindings:
        self.set_active() # resizing based on window size
        self.path.trace_add('write', self.read_dataframe)

    def update_all_graphs(self):
        """
        calls its graph components' graphing functions with appropriate parameters.
        Intended to be a global event thing that happens when we want to update all the graphs at once.
        (like when a dataset file is selected).
        """
        #print(self.df)
        if self.df is not None and self.c is not None:
            # trajectory callable needs: the fig, plot, dataframe, collection.
            traj_args = {'c' : self.c}
            self.trajectory.updateGraph(self.df, Trajectory_callable, **traj_args)
            # everything else's callable needs: the fig, plot, dataframe, id.
            # these are decided in the DropdownFigure object themselves.
            self.graph1.updateGraph(self.df)
            self.graph2.updateGraph(self.df)

    def update_dropdown(self, event, dropdown):
        """
        because the dropdown figures still need access to this object's df property, the call for it must happen from here as well.
        we will access the specific object that caused this to run from the event.

        this is running every combobox update.
        
        PARAMS:
        dropdown = the instance of DropdownFigure responsible for this trigger. 
        """
        if self.df is not None and self.c is not None:
            dropdown.update_graph_settings(event)
            dropdown.updateGraph(self.df)
    
    def read_dataframe(self, *args):
        """
        path is expected to be the full dataset path.
        The dataset is also expected to be a .json file in the 'table' orientation, as it's what the program spits out.

        If both of these conditions are met, the function updates its internal 'df' property with it.

        This function also updates the c property with the reconstructed magpylib collections object that was used in the simulation,
        which is used for graphing the trajectory.
        """
        #print(self.path.get())
        try:
            # first thing is to read the selected dataset and populate relevant properties.
            if os.path.exists(self.path.get()):
                path = self.path.get()
                self.df = pd.read_json(path, orient='table') # reads the .json file and constructs it as a pandas dataframe.
                self.c = self.File_to_Collection(path) # reconstructs the magpylib collection object that was used.
                #print(self.df)
        except:
            print(f"Plottingwindow.PlottingWindowObj.read_dataframe: provided path does not meet the requirements of being a .json file in the table orientation. BOOOOOOOOOOOOO")
        
        self.update_all_graphs()
    
    def File_to_Collection(self, path):
        """
         1. locate the coils file, assuming that path is the dir. to the json.
         2. return the coils as a magpy collection object.
        """
        proot = str(Path(path).parents[0]) # boris_<nsteps>_<simtime>_<nparts>
        #print(f"{path}, {root}")
        coilpath = os.path.join(proot, "coils.txt") # boris_<nsteps>_<simtime>_<nparts>/coils.txt
        print(coilpath)
        df=None
        
        # store coils and rotations separately, so that we can apply the rotations afterwards
        c = mp.Collection()
        df = CSV_to_Df(coilpath, converters={"Amp":tryEval, "RotationAngle":tryEval, "RotationAxis":tryEval}, isNum=False, header=0)
        #print(df)
        for i, row in df.iterrows():
            row = row.tolist()
            position = [float(row[0]), float(row[1]), float(row[2])]
            coil = Circle(position, current=float(tryEval(row[3])), diameter=float(row[4]))

            match row[5]:
                case float():
                    coil.rotate_from_angax(row[5], row[6])
                case int():
                    coil.rotate_from_angax(row[5], row[6])
                case list():
                    for i in range(len(row[5])):
                        coil.rotate_from_angax(row[5][i], row[6][i])
            
            c.add(coil)

        return c

    def set_active(self):
        """
        binds to the configure event on window size change.
        """
        # Bind window size change event to resize callback
        self.root.bind("<Configure>", self.resize_callback)

    def set_inactive(self):
        """
        Makes the object no longer care about window size changes.
        """
        self.root.unbind("<Configure>", self.resize_callback)

    def redraw_graphs(self):
        '''
        globally redraw all graphs this components is responsible for.
        '''
        # after redrawing canvas, put tight_layout on the plots so they don't cut off.
        for fig in self.figs:
            fig.tight_layout()
        for graph in self.graphs:
            graph.draw()
            

    def resize_callback(self, event):
        """
        We want to enforce the size of each graphing element.
        Not only within the window(so that they don't overflow), but also within the frame (the trajectory graph should be larger).
        """
        # get the current window width and height
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        #print(width, height)
        
        # **I'm going to measure the desired size by percentages of the window size.
        traj_width = ((width * 0.45))
        traj_height = ((height * 0.5))

        g1_width = ((width * 0.3))
        g1_height = ((height * 0.35))

        # set canvas sizes.
        # To enforce strict size limits on the mpl figures, we set the FigureCanvasTkAgg object's internal canvas widget's size.
        self.graphs[0].get_tk_widget().config(width=traj_width, height=traj_height)
        self.graphs[1].get_tk_widget().config(width=g1_width, height=g1_height)
        self.graphs[2].get_tk_widget().config(width=g1_width, height=g1_height)
        
        # redraw the graphs
        self.redraw_graphs()

def on_main_notebook_tab_changed(event, plotObj:PlottingWindowObj):
    """
    Graph resizing does not behave as expected when done on figures that are on inactive tabs.
    This is because the figures have not been rendered yet.

    Therefore, the figures need to be rendered specifically when they become active.
    """
    # get the name of the active tab.
    widget = event.widget
    tab_name = widget.tab(widget.select(), "text")
    # when the active tab is the plotting tab, then redraw the figures to ensure they render correctly.
    if tab_name == "Plot":
        # 1. make the object care about window size changes
        #plotObj.set_active()
        # 2. manually call the resize callback just this once.
        plotObj.redraw_graphs()
    else:
        # if the name of the tab is not Plot, then make sure the object is unbound from the window change event.
       #plotObj.set_inactive()
       pass


"""
deprecated because I want a more OOP approach to adding multiple figures.
"""
class TrajGraph(tk.Canvas):
    def __init__(self, master, stride_lower=1, stride_upper=100, **kwargs):
        mpl.use("tkagg")
        self.master = master
        self.title = "Trajectory"

        #Var to read currently selected Stride
        self.stride_var = tk.IntVar()

        # Instantiate canvas
        super().__init__(master, **kwargs)

        self.frame = tk.Frame(self)

        # Create slider for Stride
        stride_slider = tk.Scale(self.frame, variable=self.stride_var, 
                                 from_=stride_lower, to=stride_upper,
                                 orient="horizontal")
        stride_label = tk.Label(self.frame, text="Step Stride")
        
        # Create graph
        #self.ConstructGraph()

        self.window = self.create_window(0,0, window=self.frame, anchor="nw")

        # Packing
        stride_label.pack()
        stride_slider.pack(side="top", fill="x", expand=True)
        #self.frame.pack(side='top', fill='x', expand=True)
        #self.canvas.get_tk_widget().pack(fill="both", expand=True)
        #self.toolbar.pack(side=tk.BOTTOM, fill="x")
        #self.pack(fill="both", expand=True, side="top")

        # Bind self to re-register the scroll area upon window dimension change
        self.bind('<Configure>', self._on_Configure)

    def _on_Configure(self, event):
        """
        Intended to run whenever the root window's dimensions change.
            - resize the frame
            - update the scroll area.
        """
        # Get updated window width
        w = event.width

        # Adjust the canvas element(self) to the updated width, to match
        self.itemconfig(self.window, width = w)
    
    def ConstructGraph(self):
            """
            creates a matplotlib figure
            """
            self.fig = plt.figure()
            self.plot = self.fig.add_subplot(1,2,1, projection='3d')

            self.plot_vcross = self.fig.add_subplot(2,2,2)
            self.plot_02 = self.fig.add_subplot(2,2,3)

            #self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            #self.toolbar = NavigationToolbar2Tk(self.canvas, pack_toolbar=False)
            #self.toolbar.pack(side="bottom")
            self.fig.tight_layout()
            #self.canvas.draw()
    
    def SetAxis(self):
        self.plot_vcross.set_title('Velocity')
        self.plot_vcross.set_xlabel('Step Number')
        self.plot_vcross.set_ylabel('M/s')
        self.plot_vcross.legend(['Vel Magnitude', 'Vx', 'Vy', 'Vz'], ncol=2, fancybox=True, shadow=True, loc="upper center", bbox_to_anchor=(0.5, -0.25))

        self.plot.set_xlabel("X (m)")
        self.plot.set_ylabel("Y (m)")
        self.plot.set_zlabel("Z (m)")


    def File_to_Collection(self, path):
        """
         1. locate the coils file, assuming that path is the dir. to the json.
         2. return the coils as a magpy collection object.
        """
        proot = str(Path(path).parents[0]) # boris_<nsteps>_<simtime>_<nparts>
        #print(f"{path}, {root}")
        coilpath = os.path.join(proot, "coils.txt") # boris_<nsteps>_<simtime>_<nparts>/coils.txt
        print(coilpath)
        df=None
        
        # store coils and rotations separately, so that we can apply the rotations afterwards
        c = mp.Collection()
        df = CSV_to_Df(coilpath, converters={"Amp":tryEval, "RotationAngle":tryEval, "RotationAxis":tryEval}, isNum=False, header=0)
        #print(df)
        for i, row in df.iterrows():
            row = row.tolist()
            position = [float(row[0]), float(row[1]), float(row[2])]
            coil = Circle(position, current=float(tryEval(row[3])), diameter=float(row[4]))

            match row[5]:
                case float():
                    coil.rotate_from_angax(row[5], row[6])
                case int():
                    coil.rotate_from_angax(row[5], row[6])
                case list():
                    out = []
                    for i in range(len(row[5])):
                        coil.rotate_from_angax(row[5][i], row[6][i])
            
            c.add(coil)

        return c


    def UpdateGraph(self, label:tk.Label):
        """
        called whenever the 'plot' button is pressed. Updates the graph in the frame with the trajectory.
        """
        self.ConstructGraph()

        self.plot.cla() # reset plot
        self.plot_vcross.cla()

        # Read data at the supplied path
        path = label.cget("text")
        c = self.File_to_Collection(path) # magpy.collection object
        df = JSON_to_Df(path) # dataframe

        # Get GUI value for graph resolution
        stride = int(self.stride_var.get())

        # Color scaling based on time
        palettes = ["copper", "gist_heat"]
        nump = df["id"].max() + 1

        # Graph trajectory for each particle
        for part in range(nump):
            # extract data from dataframe
            dfslice = df[df["id"] == part]
            x, y, z = dfslice["px"].to_numpy(), dfslice["py"].to_numpy(), dfslice["pz"].to_numpy() #x, y, z coord points
            coords = np.column_stack((x,y,z))
            vx, vy, vz = dfslice["vx"].to_numpy(), dfslice["vy"].to_numpy(), dfslice["vz"].to_numpy()
            vels = np.column_stack((vx,vy,vz))
            bx,by,bz = dfslice["bx"].to_numpy(), dfslice["by"].to_numpy(), dfslice["bz"].to_numpy()
            bs = np.column_stack((bx,by,bz))

            vcrossmag, bmag, vcross_sq, vSum, v_mag, vels = CalculateLoss(vels, bs, 100)
            vcrossmag_zeros = np.where(vcrossmag == 0)
            #print(vcrossmag_zeros)

            # Apply stride by using a bool mask to get every 'stride-th' point.
            mask = np.ones(len(x), dtype=bool)
            mask[:] = False
            mask[np.arange(0, len(x), stride)] = True

            # update the x, y, z arrays with bool mask
            x = x[mask]
            y = y[mask]
            z = z[mask]
            # Color the points based on step count
            colors = mpl.colormaps[palettes[part]]
            self.plot.scatter(x,y,z, cmap=colors, c=np.linspace(0,1,len(x)), s=2.5)
            #self.plot_vcross.plot(vcrossmag)
            #self.plot_vcross.plot(bmag)
            #self.plot_vcross.plot(vcross_sq)
            #self.plot_vcross.plot(vSum)
            self.plot_vcross.plot(v_mag)
            self.plot_vcross.plot(vels)

        mp.show(c, canvas=self.plot)
        self.SetAxis()
        self.plot.get_legend().remove()
        self.fig.tight_layout()
        self.fig.show()
        #self.canvas.draw()
        #print(f'graphing finished.')


"""
Junk for integrating plotting visuals into the GUI window
"""
import pickle
import io
import magpylib as mp
from magpylib.current import Circle
from pathlib import Path
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from Gui_tkinter.funcs.GuiEntryHelpers import (JSON_to_Df, tryEval, CSV_to_Df)
import pandas as pd
from calcs.BorisAnalysis import *
from settings.notifs import Popup_Notifs, Title_Notif
from system.temp_manager import TEMPMANAGER_MANAGER
import system.temp_file_names as names
import h5py

"""
the following r settings and callables that the classes will implement.
"""
dpi = 100 # dpi of the graphs
dropdown_font_textsize_proportion = 3
trajectory_font_textsize_proportion = 4

# SETTINGS FOR NEW TOPLEVEL WINDOW GRAPH
# these are in inches.
toplevel_width = 8
toplevel_height = 4

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
    'title' : 'Trajectory',
    'zlab' : 'Z (m)',
    'ylab' : 'Y (m)',
    'xlab' : 'X (m)'
}

vel_step_style = {
    'title' : 'Vel vs. Step',
    'ylab' : 'm/s',
    'xlab' : 'step'
}

b_step_style = {
    'title' : 'B-mag vs. Step',
    'ylab' : 'T',
    'xlab' : 'step'
}

e_step_style = {
    'title' : 'E-mag vs. Step',
    'ylab' : 'V per m',
    'xlab' : 'step'
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
def Param_v_Step_callable(fig, plot, path, id, **kwargs):
    """
    for tracking a single parameter involved in the simulation as a linegraph respective to the step count.
    used for the vel, b-mag, e-mag v, step graphs.
    """
    h5_dct = {"v" : {'xn' : 'vx',
                     'yn' : 'vy',
                     'zn' : 'vz',
                     'mag_key' : 'vmag',
                     'perp_key' : 'vperp',
                     'par_key' : 'vpar',
                     'src' : '/src/velocity'},

              "b" : {'xn' : 'bx',
                     'yn' : 'by',
                     'zn' : 'bz',
                     'mag_key' : 'bmag',
                     'perp_key' : 'bperp',
                     'par_key' : 'bpar',
                     'src' : 'src/fields/b'},

              'e' : {'xn' : 'ex',
                     'yn' : 'ey',
                     'zn' : 'ez',
                     'mag_key' : 'emag',
                     'perp_key' : 'eperp',
                     'par_key' : 'epar',
                     'src' : 'src/fields/e'}}

        # the id parameter lets this function know what to look for in the dataframe.
    assert id in ('v', 'b', 'e'), f"YOU PROVIDED AN UNSUPPORTED ID TO PlottingWindow.Param_v_Step_callable!! {id} is not v, b, nor e!"

    # now that we know the column names associated with the data we want, we index the dataframe with the relevant info
    #dfslice = df[df['id'] == 0] # right now, we only look at the 1st particle.
    #x, y, z = dfslice[xn].to_numpy(), dfslice[yn].to_numpy(), dfslice[zn].to_numpy() #x, y, z coord points at each step
    with h5py.File(path, 'r+') as f:
        ds = f[h5_dct[id]['src']]
        x, y, z = ds[h5_dct[id]['xn']], ds[h5_dct[id]['yn']], ds[h5_dct[id]['zn']]
        coords = np.column_stack((x,y,z))
        #print(coords)

            # get the graphable components
            # 1. the magnitude of the component at each step.
        step_mag = magnitude_at_each_step(coords, f, h5_dct[id]['src'], h5_dct[id]['mag_key'])[:-1]
        #print(step_mag)

            # for now, b has only this line.
        if id == 'b':
            plot.plot(step_mag)
            return True
        else:
            #print("hi")
            b_ds = f[h5_dct['b']['src']]
                # everyone else gets parallel and perpendicular components also graphed, which are calculated relative to b.
            #bx,by,bz = dfslice["bx"].to_numpy(), dfslice["by"].to_numpy(), dfslice["bz"].to_numpy() # b components at each step to calculate v||, e||
            bx, by, bz = b_ds[h5_dct['b']['xn']], b_ds[h5_dct['b']['yn']], b_ds[h5_dct['b']['zn']]
            bs = np.column_stack((bx, by, bz)) # b coordinates all in one array.

                # get the parallel and perpendicular components relative to b
            step_parallel = get_parallel(bs, coords, f, h5_dct[id]['src'], h5_dct[id]['par_key'])[:-1]
            step_perpendicular = get_perpendicular(bs, coords, f, h5_dct[id]['src'], h5_dct[id]['perp_key'])[:-1]

                # graph these guys.
            plot.plot(step_mag, label='mag', color='green')
            plot.plot(step_parallel, label='p', color='blue')
            plot.plot(step_perpendicular, label='perp', color='red')

            plot.grid()
            #print(f"plotting done")

                # add a legend
            plot.legend(bbox_to_anchor=(0, 1.15), loc='lower left', fontsize=8, ncol=3 )


def Trajectory_callable(fig, plot, v1, v2, v3, path, c:mp.Collection, **kwargs):
    """
    for graphing the 3d trajectory of a single particle.
    """
    palettes = ["copper", "gist_heat"] # supported palettes for multiple particles.

    with h5py.File(path, 'r') as f:
        # get the number of particles. Because 'id' is working with a 0 index, add 1.
        #nump = df["id"].max() + 1
        nump=1
        # Graph trajectory for each particle
        df = f['src/position']
        for part in range(nump):
            # extract data from dataframe
            #dfslice = df[df["id"] == part] # only using info from the corresponding particle id.
            #x, y, z = dfslice["px"].to_numpy(), dfslice["py"].to_numpy(), dfslice["pz"].to_numpy() #x, y, z coord points at each step
            x, y, z = df["px"], df["py"], df["pz"]  # x, y, z coord points at each step
            # make the matching index's color palette a colormap distributed across the steps.
            colors = mpl.colormaps[palettes[part]]

            # actually plot everything.
                # isometric
            plot.scatter(x,y,z, cmap=colors, c=np.linspace(0,1,len(x)), s=2.5)
                # XY
            v1.scatter(x,y,z, cmap=colors, c=np.linspace(0,1,len(x)), s=2.5)
            v1.view_init(elev=90, azim=-90, roll=0)
            v1.set_title("XY Plane", pad=0)
                # YZ
            v2.scatter(x, y, z, cmap=colors, c=np.linspace(0, 1, len(x)), s=2.5)
            v2.view_init(elev=0, azim=0, roll=0)
            v2.set_title("YZ Plane", pad=0)
                # XZ
            v3.scatter(x, y, z, cmap=colors, c=np.linspace(0, 1, len(x)), s=2.5)
            v3.view_init(elev=0, azim=-90, roll=0)
            v3.set_title("XZ Plane", pad=0)

    # Additionally, we want to also show the coil configuration.
    mp.show(c, canvas=plot)
    mp.show(c, canvas=v1)
    mp.show(c, canvas=v2)
    mp.show(c, canvas=v3)

    plot.get_legend().remove()
    v1.get_legend().remove()
    v2.get_legend().remove()
    v3.get_legend().remove()

    v1.set_zlabel("")
    v2.set_xlabel("")
    v3.set_ylabel("")

    v1.get_zaxis().set_ticks([])
    v2.get_xaxis().set_ticks([])
    v3.get_yaxis().set_ticks([])



# option, style mapping, so the program knows what style goes with each option:
graph_option_style_map = {'Vel vs. Step' : {'id' : 'v', 'style': vel_step_style},
                          'B-mag vs. Step' : {'id' : 'b', 'style' : b_step_style},
                          'E-mag vs. Step': {'id' : 'e', 'style' : e_step_style}}

'''
the following r the actual classes that implement the previously established settings and functions.
'''
# Custom toolbar
class CustomToolbar(NavigationToolbar2Tk):
    """
    the same toolbar, except there is a new button that opens the canvas in its own window.
    """
        
    def open_window(self):
        """
        function to open the figure in own window.
        Also, the window CANNOT be in its own thread because matplotlib's show needs the main thread. 

        So this will open a tk.Toplevel window containing the figure instead.
        """
        # create a toplevel object.
        window = tk.Toplevel(self.root)

        # FIGURE ACCESSING/FORMATTING
        # we may need to pickle, depickle the figure to ensure we're working with an independent copy.
        buf = io.BytesIO()
        pickle.dump(self.canvas.figure, buf)
        buf.seek(0)
        fig = pickle.load(buf)

        # resize the figure copy to the global settings.
        fig.set_size_inches(toplevel_width, toplevel_height)
        
        # and then we also get a reference to the subplot so we can adjust the font sizes and stuff.
        ax = fig.get_axes()[0]
        ax.set_title(ax.get_title(), size=20)
        ax.set_xlabel(ax.get_xlabel(), size=12, labelpad=4)
        ax.set_ylabel(ax.get_ylabel(), size=12, labelpad=4)
        if ax.name == '3d':
            ax.set_zlabel(ax.get_zlabel(), size=12, labelpad=4)
        ax.tick_params(axis='both', which='major', labelsize = 10, pad=4)
        fig.tight_layout()

        # FIGURE DRAWING
        # add the figure and toolbar to the new window.
        canvas = FigureCanvasTkAgg(master=window, figure=fig)
        toolbar = NavigationToolbar2Tk(canvas, window)
        canvas.get_tk_widget().pack(side='top')
        canvas.draw()        
        
    def __init__(self,parent_, root_):
        self.root = root_ # root refers to the parent window of the TK application.
        self.toolitems += ((None, None, None, None), 
                           ("Enlarge", "Opens graph in new window", 'home', "open_window"))
        NavigationToolbar2Tk.__init__(self,parent_)



# CLASSES
from PIL import ImageTk, Image
import definitions
"""
Update as of 5/15: the trajectory plot shown in the GUI will be a static image. Interactive options will be available via button press.

The figure in this class only updates when a new dataset .json is selected. It saves the figure as an image to its corresponding tempfile,
and its canvas draws that image.
"""
class StaticFigure(tk.Frame):
    def __init__(self, master, png_path, graph_settings: dict = trajectory_style, **kwargs):
            # tk Object(s) init
        self.gs = gridspec.GridSpec(3, 2, width_ratios=[3, 1])
        super().__init__(master, **kwargs)
        self.graph_settings = graph_settings
        self.png_full_path = f"{png_path}.png"
        TEMPMANAGER_MANAGER.imgs.append(self.png_full_path)
        #self.png_full_path = os.path.join(definitions.DIR_ROOT, f"system\\imgs\\cat.png")
        self.img_frame = tk.Frame(self) # main container for the image
        self.img_label = tk.Label(self.img_frame)

            # mpl figure init
        self.initFig()

            # packing
        self.img_frame.pack()
        self.img_label.pack(side = "bottom", fill = "both", expand = "yes")
    
    """
    Called in init. 
    """
    def initFig(self):
        self.fig = plt.figure(figsize=(5,8), constrained_layout=True)
        self.gs = self.fig.add_gridspec(3, 2, width_ratios=[1, 1],wspace=0.2, hspace=0.1)
        projection = self.graph_settings['projection']
        self.plot = self.fig.add_subplot(self.gs[:, 0], projection=projection)
        self.v1 = self.fig.add_subplot(self.gs[0,1], projection=projection)
        self.v2 = self.fig.add_subplot(self.gs[1,1], projection=projection)
        self.v3 = self.fig.add_subplot(self.gs[2,1], projection=projection)
        _vs = [self.v1, self.v2, self.v3]
        for view in _vs:
            view.set_proj_type('ortho')

        # apply labels outlined in graph settings.
        self.renameLabels()

        self.fig.subplots_adjust(wspace=0.1, hspace=0.1)
    
    """
    Called in self.initFig, which is run in init.
    """
    def renameLabels(self):
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
    
    """
    Display the image in the object's image frame
    """
    def displayImage(self):
        self.im = ImageTk.PhotoImage(Image.open(self.png_full_path))
        #self.im = ImageTk.PhotoImage(Image.open(os.path.join(definitions.DIR_ROOT, f"Scripts\\system\\imgs\\cat.png")))
        #self.img_label.config(image = ImageTk.PhotoImage(Image.open(self.png_full_path)))
        self.img_label.config(image = self.im)

    """
    Clears and renames the plot.
    """
    def prepareGraph(self):
        # clear the plot of its impurities
        self.plot.cla()
        self.v1.cla()
        self.v2.cla()
        self.v3.cla()
        # replot the labels according to the settings.
        self.renameLabels()

    """
    Called only when new plotfile is chosen
    """
    def updateGraph(self, df:pd.DataFrame, func:callable, **kwargs):
        """
        When called, the selected graphing logic will be called once more.

        It is expected that the dataframe is externally provided upon the function call.
        """
        self.prepareGraph()
        func(self.fig, self.plot, self.v1, self.v2, self.v3, df, **kwargs) # the graphing logic is being applied here.
        self.gs.tight_layout(self.fig)
        self.fig.savefig(self.png_full_path, bbox_inches='tight') # save to file. Will overwrite if file exists alr.

        self.displayImage() # after saving, display the image to self.img_label (tk.Label)
        return True


class CanvasFigure(tk.Frame):
    """
    A class that contains a matplotlib figure inside of itself, navigable with tkinter.

    Also has a button that opens the graph in a dedicated window. Because oftentimes things are small.
    I think this is a good compromise between dedicated windows vs. in-program frames.
        > you control the thing graphed and see its general shape in program
        > you can then see the detailed view if you choose tol
    """

    def __init__(self, master, root, **kwargs):
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
        
        # REST OF INIT: CLASS SPECIFIC STUFF
        # Instantiate figure
        self.initFig()
        # After instantiating the figure, it can be placed in a tk.Canvas
        #self.button = tk.Button(master=self, text="Enlarge")
        #self.button.pack(side=tk.TOP)
        self.canvas = tk.Canvas(master=self)
        self.canvas.pack(side=tk.TOP, expand=1)
        self.graph = FigureCanvasTkAgg(self.fig, self.canvas)
        self.graph.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        # add the navigation toolbar
        self.toolbar = CustomToolbar(self.graph, root)

    
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

    def updateGraph(self, func:callable, path, **kwargs):
        """
        When called, the selected graphing logic will be called once more.

        It is expected that the dataframe is externally provided upon the function call.
        """
        self.prepareGraph()
        func(self.fig, self.plot, path, **kwargs) # the graphing logic is being applied here.
        return True

class DropdownFigure(tk.Frame):
    """
    A FRAME THAT WILL CONTAIN A COMBOBOX.
    THIS COMBOBOX WILL HAVE VARIOUS GRAPHING OPTIONS TO CHOOSE FROM,
    WHICH WILL AUTOMATICALLY UPDATE THE INCLUDED GRAPH.
    """
    def __init__(self, master, root, **kwargs):
        self.master = master
        super().__init__(master, **kwargs)
        # store references to children
        self.canvFig = CanvasFigure(master=self, root=root, **kwargs)
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
        self.settings = self.canvFig.graph_settings.update(new_dict)
        #print(self.settings)
    
    def updateGraph(self, path, **kwargs):
        """
        calls the updateGraph function (with identical parameters) to the CanvasFigure object.
        """
        try:
            # get the id: a value associated with the currently selected dropdown menu option.
            id = graph_option_style_map[self.chosenVal.get()]['id']

            # only do graphing stuff if id is not none; if something is acutally chosen lol.
            if id is not None:
                #print("you should be updating a dropdown graph.")
                self.canvFig.updateGraph(Param_v_Step_callable, path, id=id)
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
                         # it's also needed to make a new toplevel window for my custom toolbar button press event.
        self.master = master
        self.df = None # the dataset read from the .json output file.
        self.c = None # the magpylib.collection object that was used to run the simulation.
        self.path = label
        self._path = self.path.get()
        self._h_path = None
        super().__init__(master)
        self.config(highlightbackground='black', highlightthickness='2') # visualize frame bounds

        # we want a 3-plot structure with the trajectory plot dominating a whole column to itself.
        # Create figures.
        self.trajectory = StaticFigure(master=self, 
                                       png_path=TEMPMANAGER_MANAGER.files[names.m1f2],
                                       graph_settings=trajectory_style)
        self.trajectory.plot.set_box_aspect([1,1,1]) # make the 3d bounding box always square.
        self.graph1 = DropdownFigure(self, root)
        self.graph2 = DropdownFigure(self, root)

        # also for dropdown figures, we need to subscribe to their combobox changed events.
        # REMINDER: THIS IS SO THAT WE CAN PASS THE DATAFRAME PROPERTY FROM THIS CLASS TO THE DROPDOWNS WHILE TRIGGERING UPDATES FROM TK EVENTS.
        # update_dropdown from this class runs because of this.
        self.graph1.external_bind(self)
        self.graph2.external_bind(self)

        # Store figures and the canvases they live on.
        self.figs = [self.trajectory.fig, self.graph1.fig, self.graph2.fig] # the mpl fig object
        self.graphs = [self.graph1.graph, self.graph2.graph] # the FigureCanvasTkAgg objects
        self.plots = [self.trajectory.plot, self.graph1.plot, self.graph2.plot] # the subplots in the mpl figs
        self.canvases = [self.graph1.canvas, self.graph2.canvas] # the canvases that hold the FigureCanvasTkAggs

        # additional figure containers, for just holding the dropdown graphs.
        self.dropdown_figures = [self.graph1.fig, self.graph2.fig]
        self.dropdown_graphs = [self.graph1.graph, self.graph2.graph]

        # packing step
        self.trajectory.pack(expand=1, side=tk.LEFT, anchor="w", ipadx=3, ipady=3, padx=5)
        self.graph1.pack(side=tk.TOP, anchor='ne', expand=1, ipadx=3, ipady=3, padx=1, pady=2)
        self.graph2.pack(side=tk.TOP, anchor='se', expand=1, ipadx=3, ipady=3, padx=1, pady=2)

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
        # trajectory callable needs: the fig, plot, dataframe, collection.
        traj_args = {'c' : self.c}
        self.trajectory.updateGraph(self._h_path, Trajectory_callable, **traj_args)
        # everything else's callable needs: the fig, plot, dataframe, id.
        # these are decided in the DropdownFigure object themselves.
        self.graph1.updateGraph(self._h_path)
        self.graph2.updateGraph(self._h_path)
        self.resize_callback(None)

    def update_dropdown(self, event, dropdown):
        """
        because the dropdown figures still need access to this object's df property, the call for it must happen from here as well.
        we will access the specific object that caused this to run from the event.

        this is running every combobox update.
        
        PARAMS:
        dropdown = the instance of DropdownFigure responsible for this trigger. 
        """
        dropdown.update_graph_settings(event)
        dropdown.updateGraph(self._h_path)
        self.resize_callback(None)
    
    """
    path is expected to be the parent dir to a known .h5 file with the same structure as defined in files.hdf5.output_file_structure
    
    """
    def read_dataframe(self, *args):
        path = self.path.get()
        self._path = str(Path(path).parents[0])
        self._h_path = os.path.join(self._path, 'data.hdf5')
        self.c = self.File_to_Collection(path)  # reconstructs the magpylib collection object that was used.
        self.update_all_graphs()


    '''def read_dataframe(self, *args):
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
                #print(f"dataframe reading passed")
                self.c = self.File_to_Collection(path) # reconstructs the magpylib collection object that was used.
                #print(f"collection creaiton passed")
                #print(self.df)
            else:
                print(f"Path {path} does not exist.")
        except ValueError:
            print(f"Plottingwindow.PlottingWindowObj.read_dataframe: provided path does not meet the requirements of being a .json file in the table orientation, or the provided collection is")
        
        self.update_all_graphs()'''
    
    def File_to_Collection(self, path):
        """
         1. locate the coils file, assuming that path is the dir. to the json.
         2. return the coils as a magpy collection object.
        """
        c = mp.Collection()
        proot = str(Path(path).parents[0]) # boris_<nsteps>_<simtime>_<nparts>
        #print(f"{path}, {root}")
        coilpath = os.path.join(proot, "coils.txt") # boris_<nsteps>_<simtime>_<nparts>/coils.txt
        
        # in case the output folder does not have a coils.txt file.
        if(not os.path.exists(coilpath)):
            messagebox.showwarning(Title_Notif.warning, Popup_Notifs.err_plot_missing_coil)
            return c # return an empty collection 

        df=None
        # store coils and rotations separately, so that we can apply the rotations afterwards
        df = CSV_to_Df(coilpath, converters={"Amp":tryEval, "RotationAngle":tryEval, "RotationAxis":tryEval}, isNum=False, header=0)
        #print(df)
        for i, row in df.iterrows():
            row = row.tolist()
            position = [float(row[0]), float(row[1]), float(row[2])]
            #print(tryEval(row[6]))
            coil = Circle(position, current=float(row[3]), diameter=float(row[4]))
            #print(coil)
            match row[5]:
                case float():
                    coil.rotate_from_angax(row[5], row[6])
                case int():
                    coil.rotate_from_angax(row[5], row[6])
                case list():
                    for i in range(len(row[5])):
                        coil.rotate_from_angax(float(row[5][i]), row[6][i])
            
            c.add(coil)
       #print(c)
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

    def _redraw_graphs(self, figs, graphs, context, z=False):
        """
        internal function used to abstract the function call to redraw the object's internal figures.
        """
        size = context['font.size']
        padding = size * 0.01
        for fig in figs:
            for ax in fig.axes:
                # update title
                ax.title.set_fontsize(size)
                # x - axis
                ax.xaxis.label.set_fontsize(size*0.75) # size of text
                ax.xaxis.labelpad = padding
                # y - axis
                ax.yaxis.label.set_fontsize(size*0.75)
                ax.yaxis.labelpad = padding
                # ticks
                ax.tick_params(axis='both', which='major', labelsize = size*0.75, pad=padding)
                if(z):
                    padding = padding * 0.001
                    # in 3d graphs, also mess with z axis stuff.
                    ax.set_xlabel(ax.get_xlabel(), labelpad=padding)
                    ax.set_ylabel(ax.get_ylabel(), labelpad=padding)
                    ax.set_zlabel(ax.get_zlabel(), labelpad=padding)
                    ax.zaxis.label.set_fontsize(size*0.75)
                    ax.zaxis.labelpad = padding
                    ax.tick_params(axis='z', which='major', labelsize = size*0.75, pad=padding)
            fig.tight_layout()
        for graph in graphs:
            graph.draw()
    
    def redraw_graphs(self, mode='all', traj_rc = None, dropdown_rc = None):
        '''
        globally redraw all graphs this components is responsible for.
        '''
        modes = ['all', 'traj', 'dropdown']
        assert mode in modes, f"Value error: the mode argument {mode} not in {modes}"

        match mode:
            case 'all':
               assert (traj_rc is not None and dropdown_rc is not None)
               # in 'all' mode, the function calls itself to update the trajectory and dropdown graphs.
               #self.redraw_graphs('traj', traj_rc=traj_rc)
               self.redraw_graphs('dropdown', dropdown_rc=dropdown_rc)
            case 'traj':
                assert traj_rc is not None
                self._redraw_graphs([self.trajectory.fig], traj_rc, z=True)
            case 'dropdown':
                assert dropdown_rc is not None
                self._redraw_graphs(self.dropdown_figures, self.dropdown_graphs, dropdown_rc)

    def resize_callback(self, event):
        """
        We want to enforce the size of each graphing element.
        Not only within the window(so that they don't overflow), but also within the frame (the trajectory graph should be larger).
        """
        # get the current window width and height
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # **I'm going to measure the desired size by percentages of the window size.
        # Trajectory graph will be clamped to be a square aspect ratio, so both width and height should have the same value.
        w_h_avg = (width + height) / 2
        traj_width = ((w_h_avg * 0.45))
        traj_height = ((w_h_avg * 0.45))

        g1_width = ((width * 0.4))
        g1_height = ((height * 0.25))

        # set canvas sizes.
        # To enforce strict size limits on the mpl figures, we set the FigureCanvasTkAgg object's internal canvas widget's size.
        #self.graphs[0].get_tk_widget().config(width=traj_width, height=traj_height)
        self.graphs[0].get_tk_widget().config(width=g1_width, height=g1_height)
        self.graphs[1].get_tk_widget().config(width=g1_width, height=g1_height)

        # GET TEMP. RC STYLE CONTEXTS FOR LABEL PADDING AND SCALING.
        # font sizing will get the ratio between the length and height of the frame (in pixels) and multiply it by their respective proportions.
        w_h_ratio = width/height

        traj_font_size = trajectory_font_textsize_proportion
        #dropdown_font_size = w_h_ratio * dropdown_font_textsize_proportion
        dropdown_font_size = 12

        #print(f"{traj_font_size}")
        #print(f"{dropdown_font_size}")

        traj_rc = {'font.size' : traj_font_size, 'axes.labelpad' : traj_font_size, 'axes.titlesize' : traj_font_size}
        dropdown_rc = {'font.size' : dropdown_font_size, 'axes.labelpad' : dropdown_font_size, 'axes.titlesize' : dropdown_font_size}

        # redraw the graphs
        self.redraw_graphs('all', traj_rc = traj_rc, dropdown_rc = dropdown_rc)

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
        plotObj.resize_callback(None)
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
        self.plot_vcross.legend(['Vel Magnitude', 'Vx', 'Vy', 'Vz'], ncol=2, fancybox=True, shadow=True, loc="upper center", bbox_to_anchor=(0.5, -0.25), fontsize=8)

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


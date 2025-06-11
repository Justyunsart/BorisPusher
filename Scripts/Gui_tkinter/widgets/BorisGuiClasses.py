'''
Contains object-oriented GUI classes for general use.
Some are general, some are one time use.
'''

from Gui_tkinter.widgets.CurrentGuiClasses import *
from Gui_tkinter.funcs.GuiEntryHelpers import *
from math import copysign
from matplotlib import pyplot as plt
from settings.fields.FieldMethods import *
from settings.fields.FieldMethods_Impl import *
from mpl_toolkits.axes_grid1 import make_axes_locatable
from definitions import NAME_PARTICLES

# file stuff
from PrefFile import PrefFile
import numpy as np

# presets
from settings.defaults.coils import (preset_hexahedron, preset_mirror, preset_cusp)
from settings.configs.funcs.config_reader import runtime_configs
from system.temp_file_names import param_keys, m1f1
from system.temp_manager import TEMPMANAGER_MANAGER, update_temp, read_temp_file_dict
from functools import reduce
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

class MainWindow(tk.Frame):
    '''
    A Subclass of a tk.Frame that holds all the initialization functions; basically, whatever needs to run
    before anything else runs.
    '''
    filepath:str
    prefs:PrefFile
    initSuccess:bool
    winSize_x:int
    winSize_y:int

    def __init__(self, master, **kwargs):
        self.master = master
        super().__init__(**kwargs)
        self.winSize_x = self.winfo_screenwidth()
        self.winSize_y = self.winfo_screenheight()
        self.scrollables = []

    def update(self, **kwargs):
        """
        reregisters its scrolling area.
        """
        #print("should update scroll")
        self.master.update()
        for s in self.scrollables:
            s.RegisterScrollArea()


    #=============#
    # CONFIG INIT #
    #=============#
    """
    def _Init_Configs(self):
        '''
        On application start, populate simulation configurations.

        
        Stuff like, all available restart files, coil configurations, 
        as well as last used configs.
        (Just get the DIR where these are stored from Preferences.txt)
        '''
        # get pref file dir
        DIR_pref = os.path.join(self.filepath, "Preferences.txt")

        # read it
        with open(DIR_pref, "rb") as file:
            try:
                self.prefs = PrefFile(pickle.load(file))
            except:
                return False
        return True
    """


class ParticlePreview(EntryTable):
    '''
    An entrytable for viewing and editing particle initial condition csvs.
    '''
    def __init__(self, master, dataclass=file_particle, dir_observed = None):
        super().__init__(master, dataclass)
        self.fileWidget = FileDropdown(self.frame0, dir=dir_observed, default=self.create_default_input_file)
        self.fileWidget.grid(row=0, column=0, sticky="nsew")
        # add this class as a listener to the data changes.
        self.fileWidget.PATH.attach(self)
        
        self.saveButton.configure(command=partial(self.SaveData, self.fileWidget.dir.path.data))

        #self.Read_Data()
        #self._SetSaveEntry(self.fileWidget.fileName.get())
        self.update()

    """
    Called when self.fileWidget sees that its dir does not contain any files.
    Instantiates a file that contains default params.
    """
    def create_default_input_file(self, *args):
        # print(f"new file creation attempt")
        default_dataclass = self.data(self.frame1)  # construct dataclass with default parameters
        df = default_dataclass.get_dict(
            to_csv=True)  # we need to format this dict. so that rotations and angles are lists.
        # print(df)
        df = pd.DataFrame.from_dict(df)
        # print(df)

        def_name = "Default_Particle"
        self._SetSaveEntry(def_name)
        df.to_csv(os.path.join(os.path.join(runtime_configs['Paths']['Inputs'], NAME_PARTICLES),def_name), index=False)

    def EntryValidateCallback(self, entry):
        #print(f"BorisGuiClasses.ParticlePreview.EntryValidateCallback: self.instances is: {self.instances}")
        return super().EntryValidateCallback(entry)
    
    def NewEntry(self, *args, defaults=True):
        '''
        Suppress creating a new row on initialization.
        '''
        #print(self._instances)
        if(self.isInit):
            #print("Creating new entry", defaults, *args)
            #print(id(self._instances))
            super().NewEntry(*args, defaults = defaults)
            #print(id(self._instances))
        else:
            #print("suppressing New Entry")
            return False
    
    def Read_Data(self):
        '''
        look at the dir of the selected input file, then turn it into rows on the entry table
        '''
        self.ClearTable()

        #print("reading data")
        data = CSV_to_Df(self.fileWidget.PATH.data).values.tolist() # ideally, each sublist will be a row of params for file_particle
        #print(data)

        particles = []
        for row in data:
            particle = file_particle(self.frame1, 
                                     px = row[0], 
                                     py = row[1], 
                                     pz = row[2], 
                                     vx = row[3], 
                                     vy = row[4], 
                                     vz = row[5])
            #print(particle.py.paramDefault)
            particles.append(particle)
        
        #print(particles)
        self.SetRows(particles)
    
    def update(self, subject=None):
        '''
        rerun read data to reset the table upon the selected input file being changed.
        '''
        self.Read_Data()
        self._SetSaveEntry(self.fileWidget.fileName.get())
        self._updateTempFile(param_keys.particle_file.name, self.fileWidget.PATH.data)
        self._updateTempFile(param_keys.particle_name.name, self.fileWidget.combo_box.get())
    
    def SaveData(self, dir:str, container=None, customContainer=False):
        super().SaveData(dir, container, customContainer)

        # In addition to the super, also update the selected file's value in the field dropdown
        if self.saveEntryVal.get() not in self.fileWidget.combo_box["values"]:
            self.fileWidget.combo_box["values"] += (self.saveEntryVal.get(),)
            self.fileWidget.combo_box.current(len(self.fileWidget.combo_box["values"]) - 1)
    
    def GetData(self):
        out =  super().GetData()
        out["Particle File"] = self.fileWidget.fileName.get()
        return out
    
    def _Set(self, key, value):
        "edits the value of the dropdown widgets to the provided one."
        if(key != 'particleFile'):
            return False
        
        dropdownLst:list = self.fileWidget.combo_box["values"]
        try:
            ind = dropdownLst.index(value)
            self.fileWidget.combo_box.current(ind)
        except ValueError:
            self.fileWidget.combo_box.current(0)
    
    def init_temp(self, lu):
        if lu is not None and lu[param_keys.particle_name.name] in os.listdir(os.path.join(runtime_configs['Paths']['inputs'], NAME_PARTICLES)):
            try:
                self.fileWidget.combo_box.set(lu[param_keys.particle_name.name])
            except KeyError:
                pass
        self.update()
        

class ParticlePreviewSettings():
    '''
    checkmarks for some settings like:
        > overwrite (checked on by default)
    '''
    def __init__(self, master):
        self.master = master

        self.overwriteCheck = tk.Checkbutton(
            master=self.master,
            text="overwrite"
        )
        self.overwriteCheck.grid(row=0, column=1, sticky="W")
        self.overwriteCheck.select() #set on by default

class CoilButtons():
    '''
    helpful autofill widgets for stuff like:
        > quick setups for mirror, hexahedron

    
    This will sit next to the entry table, and will feature buttons and entries.
    '''
    table:CurrentEntryTable
    def __init__(self, master, table):
        self.master = master
        self.table = table

        # extra organizing frames
        mainframe = tk.LabelFrame(self.master,
                                  text="Common Settings")
        mainframe.grid(row=0, column=0, padx=10, pady=10, sticky="W")

        configFrames = tk.LabelFrame(master=mainframe,
                                     text="Quick Shapes")
        configFrames.grid(row=0, column=0, padx=5, pady=5, sticky="W")

        paramFrame = tk.LabelFrame(master=mainframe,
                                   text="Global Adjustments")
        paramFrame.grid(row=1, column=0, padx=5, pady=5)

        # fill in frames w thingies
        ## BUTTONS
        self.hexahedron = tk.Button(master=configFrames,
                                    text="Hexahedron")
        self.hexahedron.grid(row=0, column=0, sticky="W", padx=5, pady=5)

        self.Mirror = tk.Button(master=configFrames,
                                    text="Mirror")
        self.Mirror.grid(row=0, column=1, sticky="W", padx=5, pady=5)

        self.Cusp = tk.Button(master=configFrames,
                                    text="Cusp")
        self.Cusp.grid(row=0, column=2, sticky="W", padx=5, pady=5)

        ### Button function calls
        self.hexahedron.config(command=partial(self.table.Create_From_Preset, preset_hexahedron))
        self.Mirror.config(command=partial(self.table.Create_From_Preset, preset_mirror))
        self.Cusp.config(command=partial(self.table.Create_From_Preset, preset_cusp))

        ## PARAMS
        ### checkbox that ensures that the coil is symmetric about origin
        self.symCheck = tk.IntVar(value = 1)
        self.isSym = tk.Checkbutton(master = paramFrame,
                                    text="symmetric about origin",
                                    variable=self.symCheck)
        self.isSym.grid(row=0, column=0, sticky="W")

        ### rest of the params that gets turned on when check is true
        entryFrame = tk.Frame(paramFrame)
        entryFrame.grid(row=1, column=0)
        self.gap = LabeledEntry(master=entryFrame,
                                row=0,
                                col=0,
                                title="Offset By: ",
                                val=0.,
                                width=10,
                                name="position")
        self.dia = LabeledEntry(master=entryFrame,
                                row=1,
                                col=0,
                                title="Diameter: ",
                                val=0.,
                                width=10,
                                name="diameter")
        self.amp = LabeledEntry(master=entryFrame,
                                row=2,
                                col=0,
                                title="Current: ",
                                val=0.,
                                width=10,
                                name="amp")
        self.buttons = [self.gap, self.dia, self.amp]
        
        ### Button to apply changes - on its own frame for ease of gridding
        buttonFrame = tk.Frame(master=paramFrame)
        buttonFrame.grid(row=4, column=0, pady=10)
        self.apply = tk.Button(master = buttonFrame,
                               text="Apply",
                               command=self.apply)
        self.apply.grid(row=0, column=0, sticky= "")

    def GatherEntries(self):
        """
        returns a list of entries with actual values in them.
        """
        out = {}
        for button in self.buttons:
            if float(eval(button.entry.get())) != 0.:
                out[button.entry._name] = button.entry.get()
        return out
    
    def apply(self):
        '''
        when pressing the apply button, the program will determine
        which operations should be processed and execute them accordingly.
        '''
        inds = {"diameter":4,
                "amp":3}
        buttons = self.GatherEntries()
        for name, value in buttons.items():
            if name == "position":
                self._GapOffset(gapVal=float(value))
            elif name in inds.keys():
                self._ModifyFeature(inds[name], value)
            else:
                print(f'CoilButtons.GatherEntries somehow ran with unrecognized tk.Entry name')
        self.table.Refresh()


    def _ModifyFeature(self, col, val):
        """
        col = index of variable to edit
        val = val to change it to
        """
        # all the widgets in the column of interest, with the title
        # headings taken out.
        widgets = self.table.frame1.grid_slaves(column=col)[::-1]
        widgets.pop(0)

        # make everything in the column the desired value
        # also multplied by the sign of the value to preserve opposing currents.
        widgets[:] = map(lambda x: (x.var.set(float(eval(val)) * copysign(1, float(eval(x.get()))))), widgets)
    
    def _GapOffset(self, gapVal:float):
        """
        logic for modifying gap


        inds: dict of inds of [x,y,z]
            > keys are rotation axis of the current loop
            > values are axes to modify
        """
        inds = {"y":0,
                "x":1,
                "z":2}
        entries = self.table.GetEntries()
        self.table.setLim(gapVal)
        for i in range(len(entries)):
            #print(entries[i])
            entry = entries[i]
            position = np.array((entry['PosX'], entry['PosY'], entry['PosZ']), dtype=float)
            ax = np.argmax(abs(position))

            # add if positive, subtract if negative
            widget = self.table.frame1.grid_slaves(column=ax, row=i+1)[0]

            current = float(widget.var.get())
            sign = float(copysign(1, current))

            widget.var.set((sign * gapVal))

class CurrentConfig:
    def __init__(self, master, DIR, Gframe):
        #print(f"BorisGuiClasses.CurrentConfig: Config is initializing.")
        self.master = master

        # frames setup
        mainframe = tk.Frame(self.master)
        mainframe.grid(row=0, column = 0)
        
        """
        plethora of frames to organize all the current file, table objects
        """
        CurrentTable = tk.Frame(mainframe)
        CurrentTable.grid(row=1, column=1, sticky="NW")

        CurrentEntry = tk.Frame(CurrentTable)
        CurrentEntry.grid(row=1, column=0)

        CurrentFile = tk.Frame(CurrentTable)
        CurrentFile.grid(row=0, column=0, sticky="NW")

        CurrentGraph = Gframe
        
        """
        this one contains all the common global transformations u can desire
        """
        ParamFrame = tk.Frame(mainframe)
        ParamFrame.grid(row=1, column=0)
        
        self.table = CurrentEntryTable(master=CurrentEntry, 
                            dataclass=CircleCurrentConfig,
                            graphFrame=CurrentGraph,
                            DIR = DIR,
                            collection_key=param_keys.mag_coil.name,
                            path_key=param_keys.coil_file.name,
                            name_key=param_keys.coil_name.name)
        
        self.param = CoilButtons(ParamFrame,
                                 table=self.table)
        
    def GetData(self):
        return self.table.GetData()
    
    def _Set(self, key:str, value:str):
        "edits the value of the dropdown widgets to the provided one."
        if(key != 'coilFile'):
            return False
        
        dropdownLst:list = self.dropdown["values"]
        try:
            ind = dropdownLst.index(value)
            self.dropdown.current(ind)
            self.table.update()
        except ValueError:
            self.dropdown.current(0)
            self.table.update()
    
    def update(self, *args, **kwargs):
        """
        Upon switching notebook tabs, I discovered something annoying. Though Tkinter has already loaded in the CurrentEntryTable,
        it still uses internal vars from the ParticlePreview.

        For example, editing a cell calls ParticlePreview's internal self.entries property, and nothing is actually changed. 
            -Calling CurrentEntryTable exclusive funcs fixes it. (opening the rotations window)
            -Loading a new coil config file also fixes it.
                >This is possibly a weird interaction between notebooks and switching between tabs containing sibling classes.
        
        To bypass this issue (as it seems to be due to the package), the program will call this function to 'refresh' the entry table widget
        when it detects the tab switching event (bound in BorisGui.py). 
        """
        #print(f"BorisGuiClasses.CurrentConfig: Update table")
        self.table.update()
    
    def init_temp(self, lu):
        self.table.init_temp(lu)


class FieldDropdown(Dropdown):
    options:Enum
    def __init__(self, master, options:Enum, label, key=None, **kwargs):
        self.options = options
        self.key = key # the field name for the temp file
        names = options._member_names_
        super().__init__(master, names, label=label, **kwargs)
        if self.key is not None:
            self.chosenVal.trace_add('write', self.update_tempfile)

    """
    updates the tempfile with the associated field method used (magpy, zero, etc.)
    """
    def update_tempfile(self, event, *args):
        d = {param_keys.method.name: self.chosenVal.get()}
        update_temp(TEMPMANAGER_MANAGER.files[m1f1], d, nested=True, key=[param_keys.field_methods.name, self.key])

    def GetData(self):
        return {str(self.options.__name__):self.chosenVal.get()}

    def _Set(self, key, value):
        try:
            ind = self.dropdown['values'].index(value)
        except:
            #print(self.dropdown['values'])
            print(f"dropdown value not found")
            return False
        #print(f"setting dropdown to: {ind}")
        self.dropdown.current(ind)
        return True
    
    def init_temp(self, lu):
        if lu is not None:
            try:
                self.dropdown.set(lu['field_methods'][self.key]['method'])
            except KeyError:
                pass
        self.update_tempfile(None)


class FieldCoord_n_Graph():
    """
    Graph, widget controls for field methods.
    """
    fig = None
    plot = None
    canvas = None
    instances:dict
    
    def __init__(self, root, table:FieldDropdown, graphOptions:FieldDropdown, graphFrame:tk.LabelFrame, canvasFrame:tk.Frame, currentTable:CurrentEntryTable,
                 title="title", x_label="x", y_label="y"):
        """the b-field parameters inside the field_methods dictionary
        expects an instance of a coordinate table, and a frame where the graph will be made.
        """
        self.root = root # reference to the main window
        self.instances = {} # holds instances of the FieldMethods_Impl class.
        self.frame = graphFrame # frame that holds the graphical button controls
        self.canvasFrame = canvasFrame # frame that holds the canvas for the actual figure
        self.currentTable = currentTable # we need a reference to the table containing the coil info so we can do B-field calcs.
        self.table = table # this table is the dropdpown menu for the fields.
        self.options = graphOptions # this is the dropdown where people choose the graph to display on the canvasFrame
        
        # properties for the graph
        self.title = title
        self.x_lab = x_label
        self.y_lab = y_label

        self.ConstructGraph()
        self.prevVal = table.chosenVal.get()

        table.chosenVal.trace_add("write", self.WidgetVisibility)
        #table.chosenVal.trace_add("write", self.UpdateGraph) # add another trace to the given table.
        
        # instantiate intialized val's widget
        self._checkInstance(self.prevVal).ShowWidget()

    def WidgetVisibility(self, *args):
        """
        check if you should toggle widget visibility on or off or not
        """
        # If you chose the same value as before, don't do anything.
        # Should theoretically never trigger if the 'write' trace doesn't trigger
        # when the same option is selected again on a ttk.Combobox
        if (self.prevVal == self.table.chosenVal):
            return True
        
        # set the previous widget to 'off'
        prev = self.prevVal
        self._checkInstance(prev).HideWidget()

        # set the current widget to 'on'
        curr = self.table.chosenVal.get()
        self._checkInstance(curr).ShowWidget()

        # then, update the tempfile (field_methods/E/params)
        d = {param_keys.params.name:
             self._checkInstance(self.table.chosenVal.get()).GetData()[self.table.chosenVal.get()]}
        update_temp(TEMPMANAGER_MANAGER.files[m1f1], d, nested=True, key=[param_keys.field_methods.name, param_keys.e.name])

        # lastly, update the prevVal property
        self.prevVal = curr

        return True
        

    def ConstructGraph(self):
        """
        creates a matplotlib figure
        """
        self.fig = plt.figure(figsize=(5,4))
        self.plot = self.fig.add_subplot(1,1,1)
        self.cax = make_axes_locatable(self.plot).append_axes("right", size="5%", pad=0.05)

        self.updateGraphButton = tk.Button(master=self.frame, text="Update Graph", command=self.UpdateGraph)
        self.updateGraphButton.grid(row=0, column=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvasFrame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        
        # have everything be off by default
        self.plot.set_axis_off()
        self.cax.set_axis_off()

    
    def _RemoveColorbar(self):
        """
        A helper function when resetting the gui plots.
        Because colorbars are added as a separate axis from the plotting one, clearing the
        plotting axis will not remove colorbars.

        Instead, this function will check the label of the last axis on the figure.
        If it's a colorbar label, then it will be removed.
        """
        # Colorbar checking
        last_axis_label = self.fig.axes[-1].get_label() # colorbar is assumed to be the last added axis. So we check the last axis label for existing colorbars.

        # Only create a colorbar if there isn't one detected at the end of the figure.
        if last_axis_label == "<colorbar>":
            ax = self.fig.gca()
            ax.images[-1].colorbar.remove()

    def UpdateGraph(self, *args):
        """
        calls the given graph method and draws it on the graph.
        Assumes that the function takes a mpl subplot as an input.
        """
        # INITIAL CHECKERS
        # Check if the graph should be edited by looking at the widget's flags.
        curr = self.table.chosenVal.get()
        doUpdate = self._checkInstance(curr).autoUpdate
        # Also check the currently selected graph value in the options dropdown.
        graphOption = self.options.chosenVal.get()
        #print(graphOption)

        # clear plot
        self.plot.cla()
        self.cax.cla()
        # set axis on
        self.plot.set_axis_on()
        match graphOption:
            case "E":
                self.cax.set_axis_on()
                """
                doUpdate is a flag set in each fieldImpl class. It used to stand for something else, but is now functionally a way to
                differentiate between functions that require a reference to the magpylib collection object or not.

                eg. Fw only gets its limits from the currentTable reference's getLim function, so it doesn't need the collection.
                Bob_e_impl needs each coil center and rotation, so it's easier to get a reference.
                """
                if doUpdate == True:
                    # gather data
                    self.SetLabels(self.plot)
                    lims = self.currentTable.getLim()

                    # plot
                    self._checkInstance(self.table.chosenVal.get()).graph(plot = self.plot, fig = self.fig, lim = lims)
                    self.canvas.draw()
                else:

                    # run the graph function
                    #print(f"collection is: {c.children_all[0].position}")
                    self._checkInstance(self.table.chosenVal.get()).graph(plot = self.plot, fig = self.fig, lim = None, cax=self.cax)
                    self.canvas.draw()
            case "B":
                """
                Plots a streamplot of the B field; a 2D cross section at a plane crossing the origin.
                """
                self.cax.set_axis_on()
                self.currentTable.GraphB(fig=self.plot, root=self.fig, cax=self.cax)
                self.canvas.draw()
            case "E_B_lineout":
                """
                Plots two line graphs comparing the magnitudes of the B and E fields across an axis.

                The graph will run coordinates on a line running through the coil center(s)
                Does not currently have the ability to select different axes in the case of multiple orientations.
                """
                self.cax.set_axis_off()
                # Check instance. Use either a pre-populated value or the default (if not instantiated).
                try:
                    self.instances["Bob_e"]
                except:
                    """
                    There is no active instance of the Bob_e object (switch the active option to Bob_e)
                    """
                    self.table._Set(2, "Bob_e")

                # Get relevant parameters
                lim = self.currentTable.getLim() + 2 # add extra padding on the x (local) axis
                axis = self.currentTable.axis # index of the major axis
                instance = self.instances["Bob_e"]
                data = instance.GetData()["Bob_e"]
                coils = data['collection']
                res = int(data['res'])

                # Generate points
                lin = np.linspace(-lim, lim, res)
                coords = np.zeros((3, res))
                coords[axis] = lin
                coords = coords.T

                # Get data
                B = self.currentTable.collection.getB(coords) # (n, 3 shape)
                # Get B magnitudes
                B = np.linalg.norm(B, axis=1)
                E = bob_e_impl.fx_calc(coords, coils, res)["sum"]

                # Plot
                self.plot.plot(lin, B, linestyle="dashed", color="blue", label="B-mag")
                self.plot.plot(lin, E, linestyle="solid", color="red", label="E-mag")
                self.plot.legend(loc="upper left")

                # Set labels
                axes = ["x", "y", "z"]
                self.plot.set_xlabel(f"{axes[axis]}-Coordinates (m)")
                self.plot.set_ylabel(f"Magnitude")
                self.plot.set_title(f"E, B lineout")

                # Add some text
                self.plot.text(1.125, 0.9, f"coords: {coords[0]} to {coords[-1]}", fontsize=10,
                               horizontalalignment='right', verticalalignment='bottom',
                               transform=self.plot.transAxes) # what coordinates were plugged in

                self.canvas.draw()
            case 'E_Streamline':
                from Alg.polarSpace import toCart, toCyl
                from copy import deepcopy
                # Generate a grid of points in a cross-section plane
                # Get the E field values at all of these points
                # Turn this data into a streamplot
                # Because the analytic equation zonks out near 0s, we need to just. translate everything away from it

                    # Will use the colorbar for this
                self.cax.set_axis_on()

                    # Get axis limits and other high level info
                lim = self.currentTable.getLim() + 1
                instance = self.instances["Bob_e"]
                data = instance.GetData()["Bob_e"]
                coils = deepcopy(data['collection'])
                res = int(data['res'])
                #print(coils.children)
                    # move coils to accommodate
                for c in coils:
                    c.position += [lim, lim, lim]

                    # construct grid for cross-section
                x = np.linspace(0, lim * 2, 100)
                z = np.linspace(0, lim * 2, 100)
                y = np.array(np.ones(100) * lim)

                grid = np.array(np.meshgrid(x, y, z)).T  # shape = (100, 100, 3, 1)
                grid = np.moveaxis(grid, 2, 0)[0]  # shape = (100, 100, 3)
                X, _, Z = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)
                X = X-(lim)
                Z = Z-(lim)
                grid = grid.reshape(100*100, 3) # shape= (100*100, 3)

                    # get E results from the grid
                Es = []
                Ex = []
                Ez = []
                for point in grid:
                        # get the point's E field value
                    #print(point)
                    #_cyl = toCyl(point)
                    _E, _cyl = bob_e_impl._ecalc(point, coils, res, sums=False) # [z, r]
                        # convert into cartesian coords from cyl coords and append it to the results
                        # since this is in the XZ plane, ignore the y axis
                    cart = toCart(_E[1], _cyl[1], _E[0]) # [r, th, rho]
                    Es.append(cart)
                    Ex.append(cart[0])
                    Ez.append(cart[2])

                    # graph the streamline plot
                #print(np.array(Ex).shape)
                #print(np.array(X).shape)
                #print(Es)
                plt = self.plot.streamplot(np.array(X), np.array(Z), np.array(Ex).reshape(100, 100), np.array(Ez).reshape(100, 100),
                                           color=np.log(np.linalg.norm(Es, axis=1)).reshape(100, 100), density=1)
                #plt = self.plot.quiver(np.array(X), np.array(Z),
                #                       np.array(Ex).reshape(100, 100), np.array(Ez).reshape(100, 100),
                #                       np.log(np.linalg.norm(Es, axis=1)).reshape(100, 100),
                #                       units='width')
                #self.plot.quiverkey(plt, 0.9, 0.9, 2, 'E', coordinates='figure')

                self.plot.set_xlabel("X-axis (m)")
                self.plot.set_ylabel("Z-axis (m)")
                self.plot.set_title("E. Field Cross Section on the X-Z plane at Y=0", pad=20)

                cbar = self.fig.colorbar(plt.lines, cax=self.cax)
                cbar.ax.set_title('log. of E-norm')

                self.canvas.draw()

    
    def update(self):
        # expected function to run when coordtable's trigger_listener is invoked.
        self.UpdateGraph() # draw the graph

    def SetLabels(self, ax):
        ax.set_title(self.title)
        ax.set_xlabel(self.x_lab)
        ax.set_ylabel(self.y_lab)
    
    def _checkInstance(self, name:str):
        """
        if exists as instance, access and return it
        if not, create one and add a ref to the instances dict.
        """
        if name in self.instances:
            # name is found in instances, return the instance
            return self.instances[name]
        else:
            # if not, create an instance.
            self.instances[name] = self.table.options[name].value(self.table.master, self.root)
            #self.instances[name].widget.add_listener(self)
            return self.instances[name]
        
    def GetData(self):
        """
        Gets the currently selected dropdown's values and passes it on as a dictionary.
        """
        return {str(self.table.options.__name__):self._checkInstance(self.table.chosenVal.get())}
    
    def _Set(self, key='E-field', method=None, params=None):
        """
        when loading in last used values, populate the given widget's entries automatically.

        EXPECTED INPUT:
        key = E-Field, value = {'Fw': {'A': '0.2', 'B': '02'}}
        """
        #value = literal_eval(value)
        # set the dropdown first
        #print(f'setting e field to: {method}')
        #self.table._Set(key, method)
        if method == "Zero":
            return True
        # set the entries.
        if params is not None:
            for k, v in params.items():
                self._checkInstance(self.table.chosenVal.get()).Set(k, v)
        return True
    
    def init_temp(self, lu):
        if lu is not None:
            try:
                self._Set(lu[param_keys.field_methods.name]['e']['method'], lu[param_keys.field_methods.name]['e']['params'])
            except KeyError:
                pass
        self.WidgetVisibility()

def _Try_Float(list):

    '''
    ask for forgiveness, not for permission.
    '''
    for word in list:
        try:
            float(word)
        except ValueError:
            return False
    
    return True

def OnNotebookTabChanged(event, *args, **kwargs):
    """
    Event function to run whenever notebook tabs are changed (from params to coil config).
    Put logic here you want to run anytime this happens.

    Things that happen right now:
    1. Depending on the tab, the active entrytable will run its update function. This ensures that tkinter treats them differently.
    """
    # Get the notebook widget.
    nb = event.widget
    # Get the currently selected tab by index
    activeTabInd = nb.index("current")

    # Get the selected tab's children widgets, and select the scrollablewidget instance. It is assumed all tabs have it.
    scollFrame = nb.winfo_children()[activeTabInd].winfo_children()[1]

    scollFrame._notify_Subscribers()
    #print(f"BorisGuiClasses.OnNotebookTabChanges: subs notified.")
    #print(activeWidgets)


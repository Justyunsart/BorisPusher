'''
Contains object-oriented GUI classes for general use.
Some are general, some are one time use.
'''

import tkinter as tk
from tkinter import ttk
from CurrentGuiClasses import *
from GuiEntryHelpers import *
from GuiHelpers import CSV_to_Df
from math import copysign
from matplotlib import pyplot as plt
from FieldMethods import *

# file stuff
from PrefFile import PrefFile
from pathlib import Path
import os
import pickle
import ast
import numpy as np

############
# MENU BAR #
############
class ConfigMenuBar():
    def __init__ (self, master):
        self.master = master

        self.InitUI()

        if not master.initSuccess:
            self._Enforce_Default()

    def InitUI(self):
        menubar = tk.Menu(self.master, tearoff=0)
        self.master.master.config(menu=menubar)

        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Preferences")
        fileMenu.add_command(label="Enforce Default",
                             command=self._Enforce_Default)


        menubar.add_cascade(label="File", menu=fileMenu)

    def _Enforce_Default(self):
        '''
        Restore default DIR paths for preference settings.
        These are written and stored in the '/Preferences.txt' file.
        '''
        # 1: Get the path of the Preferences.txt file using MainWindow (expected master)'s cwd field.
        prefPath = os.path.join(self.master.filepath, "Preferences.txt")

        # 1.5: Get the default DIRs
            ## location of inputs folder
        inputPath = os.path.join(self.master.filepath, "Inputs")

            ## location of particle condition folder
        particlePath = os.path.join(inputPath, "Particle Conditions")
        coilPath = os.path.join(inputPath, "Coil Configurations")
        coilDefsPath = os.path.join(coilPath, "Defaults")

            ## location of output folder
        outputPath = os.path.join(self.master.filepath, "Outputs")
        lastusedPath = os.path.join(inputPath, "lastUsed")

        # 2: Create the PrefFile object with default params
        prefs = PrefFile(particlePath, 
                         coilPath, 
                         coilDefsPath,
                         outputPath,
                         lastusedPath,
                         "0.000001",
                         "50000",
                         "",
                         "")
        self.master.prefs = prefs
     
        # 3: If the Pref file does not exist, create one. If it does, rewrite it.
        with open(prefPath, 'wb') as file:
            pickle.dump(prefs, file)

class Preferences():
    '''
    the window that pops up when you click the "Preferences" label in the menubar.

    has options to configure save file locations and other backend-related features.
    '''
    def __init__(self, master):
        self.master = master

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
        # number 1: know the PATH of the program's root.
        self.filepath = str(Path(__file__).resolve().parents[1]) #Expected: '/BorisPusher/...'

        super().__init__(**kwargs)
        self.winSize_x = self.winfo_screenwidth()
        self.winSize_y = self.winfo_screenheight()
        
        self.initSuccess = self._Init_Configs()

    #=============#
    # CONFIG INIT #
    #=============#
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

class Particle_File_Dropdown(FileDropdown):
    def __init__(self, master, dir, last=0, **kwargs):
        self.master = master

        self.frame = tk.Frame(master=self.master)
        self.frame.grid(row=0, column=0)

        super().__init__(self.frame, dir, last, **kwargs)
        super().grid(row=0, column=1)

        self.label = tk.Label(self.frame,
                              text="File: ")
        self.label.grid(row=0, column=0)

class TimeStep_n_NumStep():
    '''
    screw it, i'm gonna make classes for everything. Why not
    '''
    simTime:float
    simVar:tk.StringVar

    responses = {
        "good" : "everything looks good!",
        "bad" : "dt is too big."
    }

    def __init__(self, master, table:CurrentEntryTable):
        self.table = table
        self.master = master

        self.frame = tk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="W")
        self.master.grid_columnconfigure(0, weight=1)
        
        # Frame for holding check warning
        self.frame1 = tk.Frame(self.frame)
        self.frame1.grid(row=4, column=0)

        self.dt_str = tk.StringVar()
        self.dt_label = tk.Label(self.frame1,
                                 textvariable=self.dt_str)
        self.dt_label.grid(row=0, column=0)

        self.dt = LabeledEntry(self.frame, val=0.0000001, row=1, title="Timestep (sec): ", width = 10)
        self.dt.value.trace_add("write", self._Total_Sim_Time)
        self.dt.value.trace_add("write", self.dt_Callback)
        
        self.numsteps = LabeledEntry(self.frame, val=50000, row=0, title="Num Steps: ", width = 10)
        self.numsteps.value.trace_add("write", self._Total_Sim_Time)

        # display the simulation time
        self.simFrame = tk.LabelFrame(self.master, text="Total Sim Time: ", bg="gray")
        self.simFrame.grid(row=0, column=1, sticky="E")
        self.simFrame.grid_rowconfigure(0, weight=1)
        self.simFrame.grid_columnconfigure(0, weight=1)

        self.simVar = tk.StringVar()
        self._Total_Sim_Time()
        self.simLabel = tk.Label(self.simFrame,
                                 textvariable=self.simVar,
                                 justify="center")
        self.simLabel.grid(row=0, column=0, sticky="")

        table.lim.attach(self)
        #self.dt_Callback()

    def update(self, *args):
        """
        when the 'lim' Data in the current table is updated, you have to re-run the Dt size check.
        """
        self.dt_Callback()
    
    def dt_Callback(self, *args):
        lim = self._Check_Timestep_Size()
        if (float(self.dt.value.get()) < lim):
            self.dt_str.set(self.responses["good"])
        else:
            self.dt_str.set(f'Dt is too big, upper lim is: {lim}')
        
    
    def _Total_Sim_Time(self, *args):
        dt = self.dt.value.get()
        numsteps = self.numsteps.value.get()


        if(_Try_Float([dt, numsteps])):
            dt = float(dt)
            numsteps = float(numsteps)

            self.simTime = dt * numsteps
            self.simVar.set(str(self.simTime))
            return True
        return False
    
    def GetData(self):
        '''
        returns relevant data in a readable format
        '''
        data = {}
        data["numsteps"] = float(self.numsteps.entry.get())
        data["dt"] = float(self.dt.entry.get())
        return data
    
    def _Set(self, key:str, value:list):
        match key:
            case 'numsteps':
                self.numsteps.value.set(value)
            case 'timestep':
                self.dt.value.set(value)

    def _Check_Timestep_Size(self):
        """
        make sure that the timestep is sufficient.
        """
        distance = self.table.getLim() * 2 #Assuming that the coils are symmetric about origin
        #print(distance)
        desired_steps = 100
        desired_rate = 10e6

        dt_lim = distance/(desired_steps * desired_rate)
        
        return dt_lim


class ParticlePreview(EntryTable):
    '''
    An entrytable for viewing and editing particle initial condition csvs.
    '''
    def __init__(self, master, fileWidget, dataclass=file_particle):
        self.fileWidget = fileWidget
        # add this class as a listener to the data changes.
        fileWidget.PATH.attach(self)

        super().__init__(master, dataclass)
        self.saveButton.configure(command=partial(self.SaveData, self.fileWidget.dir))

        self.Read_Data()
        self._SetSaveEntry(self.fileWidget.fileName.get())
    
    def NewEntry(self, *args, defaults=True):
        '''
        Suppress creating a new row on initialization.
        '''
        if(self.isInit):
            #print("Creating new entry", defaults, *args)
            super().NewEntry(*args, defaults = defaults)
        else:
            #print("suppressing New Entry")
            return False
    
    def Read_Data(self):
        '''
        look at the dir of the selected input file, then turn it into rows on the entry table
        '''
        

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
    
    def update(self, subject):
        '''
        rerun read data to reset the table upon the selected input file being changed.
        '''
        self.Read_Data()
        self._SetSaveEntry(self.fileWidget.fileName.get())
    
    def SaveData(self, dir:str, container=None, customContainer=False):
        super().SaveData(dir, container, customContainer)

        # In addition to the super, also update the selected file's value in the field dropdown
        if self.saveEntryVal.get() not in self.fileWidget["values"]:
            self.fileWidget["values"] += (self.saveEntryVal.get(),)
            self.fileWidget.current(len(self.fileWidget["values"]) - 1)
    
    def GetData(self):
        out =  super().GetData()
        out["Particle File"] = self.fileWidget.fileName.get()
        return out
    
    def _Set(self, key, value):
        "edits the value of the dropdown widgets to the provided one."
        if(key != 'particleFile'):
            return False
        
        dropdownLst:list = self.fileWidget["values"]
        ind = dropdownLst.index(value)
        self.fileWidget.current(ind)

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

"""
WILL BE DEPRECATED
"""
class E_CoordTable(CoordTable):
    """
    extension of the coordtable class to add converse A, B vars
    used in the analytic E-field.
    """
    def __init__(self, master, title="coords", **kwargs):
        super().__init__(master, title, doInit=False, **kwargs)
        self.A = LabeledEntry(self.frame1, 1, row=2, col=0, title="A: ", width=10)
        self.B = LabeledEntry(self.frame1, 1, row=2, col=4, title="B: ", width=10)
        self.converseEntries = [self.A.entry, self.B.entry]

        self.CheckEditability()
        self.A.value.trace_add("write", self.trigger_listener)
        self.B.value.trace_add("write", self.trigger_listener)
    
    def CheckEditability(self, *args, **kwargs):
        useState = self.doUse.get()

        if(useState == 0):
            '''
            useState is off: all entries should be read-only.
            '''
            for entry in self.entries:
                entry.config(state="disabled")
            for entry in self.converseEntries:
                entry.config(state='normal')
        else:
            '''
            entries are otherwise editable.
            '''
            for entry in self.entries:
                entry.config(state="normal")
            for entry in self.converseEntries:
                entry.config(state='disabled')
    
    def GraphE(self, plot, fig, lim, *args):
        try:
            #print(f'A is: {self.A.value.get()}')
            #print(f'B is: {self.B.value.get()}')
            #print(f'Lim is: {lim}')
            A = float(self.A.value.get())
            B = float(self.B.value.get())

            lim = abs(lim)
            glim = 1.5 * lim
            x = np.linspace(-glim, glim, 50)
            # equation for fw_E
            E = np.multiply(A * np.exp(-(x / B)** 4), (x/B)**15)
            #print(f'X axis is: {x}')
            #print(f'Y axis is: {E}')
            plot.plot(x,E)
            
            # also plot vertical lines for where the coils are, for visual clarity
            plot.axvline(x = lim, color='r', linestyle='dashed')
            plot.axvline(x = -lim, color='r', linestyle='dashed')

        except ValueError:
            pass

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

        ### Button function calls
        self.hexahedron.config(command=partial(self.table.Create_Mirror, fileName="Hexahedron", templateName="hexahedron"))
        self.Mirror.config(command=partial(self.table.Create_Mirror, fileName="Mirror", templateName="mirror"))

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
            posInd = inds[entries[i]["RotationAxis"]]

            # add if positive, subtract if negative
            widget = self.table.frame1.grid_slaves(column=posInd, row=i+1)[0]

            current = float(widget.var.get())
            sign = float(copysign(1, current))

            widget.var.set((sign * gapVal))

class CurrentConfig:
    def __init__(self, master, DIR, DIR_CoilDef, Gframe):
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

        CurrentGraph = tk.Frame(Gframe)
        CurrentGraph.grid(row=2,column=0)
        
        """
        this one contains all the common global transformations u can desire
        """
        ParamFrame = tk.Frame(mainframe)
        ParamFrame.grid(row=1, column=0)
        
        # populate frames
        self.dropdown = Particle_File_Dropdown(master=CurrentFile,
                                               dir = DIR)
        
        self.table = CurrentEntryTable(master=CurrentEntry, 
                            dataclass=CircleCurrentConfig, 
                            dirWidget=self.dropdown,
                            graphFrame=CurrentGraph,
                            defaults = DIR_CoilDef)
        
        self.param = CoilButtons(ParamFrame,
                                 table=self.table)
        
    def GetData(self):
        return self.table.GetData()
    
    def _Set(self, key:str, value:str):
        "edits the value of the dropdown widgets to the provided one."
        if(key != 'coilFile'):
            return False
        
        dropdownLst:list = self.dropdown["values"]
        ind = dropdownLst.index(value)
        self.dropdown.current(ind)

    """
    CURRENTLY UNUSED BECAUSE IT TAKES WAY TOO LONG TO CALL SO OFTEN.
    might have to repurpose to something that runs from a button press instead of updating all the time.
    """
    def GraphB(self, fig, root):
        """
        with a mpl subplot as an input, graph the currently selected magnetic coil's B field's cross section.
        """
        c = self.GetData()

        # construct grid for the cross section
        x = np.linspace(-5, 5, 50) # these represent LOCAL x and y for the 2D graph, not the 3D space.
        y = np.linspace(-5, 5, 50)

        # calculate B field for the entire grid
        Bs = np.array([[c.getB([i, 0, j]) for i in x] for j in y]) # [bx, by, bz]
        '''
        Bs shape: (step, step, 3)
        '''
        # gather arguments for the streamplot
        X, Z = np.meshgrid(x, y)
        U, V = Bs[:, :, 0], Bs[:, :, 2]

        Bamp = np.sqrt(U**2 + V**2)

        stream = fig.streamplot(X, Z, U, V, color= Bamp, density=1)
        #stream = fig.streamplot(X, Z, U, V, color= Bamp, density=2, norm=colors.LogNorm(vmin = Bamp.min(), vmax = Bamp.max()))
        fig.set_xlabel("X-axis (m)")
        fig.set_ylabel("Z-axis (m)")
        fig.set_title("Magnetic Field Cross Section on the X-Z plane at Y=0")
        root.colorbar(stream.lines)

class FieldDropdown(Dropdown):
    options:Enum
    def __init__(self, master, options:Enum, label, **kwargs):
        self.options = options
        names = options._member_names_
        super().__init__(master, names, label=label, **kwargs)
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

class FieldCoord_n_Graph():
    """
    vars for the graph
    """
    fig = None
    plot = None
    canvas = None
    instances:dict
    
    def __init__(self, table:FieldDropdown, graphFrame:tk.LabelFrame, currentTable:CurrentEntryTable,
                 title="title", x_label="x", y_label="y"):
        """
        expects an instance of a coordinate table, and a frame where the graph will be made.
        """
        self.instances = {}
        self.frame = graphFrame
        self.currentTable = currentTable
        self.table = table
        self.title = title
        self.x_lab = x_label
        self.y_lab = y_label

        self.ConstructGraph()
        self.prevVal = table.chosenVal.get()

        table.chosenVal.trace_add("write", self.WidgetVisibility)
        table.chosenVal.trace_add("write", self.UpdateGraph) # add another trace to the given table.
        
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

        # lastly, update the prevVal property
        self.prevVal = curr
        return True
        

    def ConstructGraph(self):
        """
        creates a matplotlib figure
        """
        self.fig = plt.figure(figsize=(5,4))
        self.plot = self.fig.add_subplot(1,1,1)
        
        # set graph labels
        self.SetLabels(self.plot)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
    
    def UpdateGraph(self, *args):
        """
        calls the given graph method and draws it on the graph.
        Assumes that the function takes a mpl subplot as an input.
        """
        # gather data
        self.plot.cla()
        self.SetLabels(self.plot)
        lims = self.currentTable.getLim()

        # plot
        self._checkInstance(self.table.chosenVal.get()).graph(plot = self.plot, fig = self.fig, lim = lims)
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
            self.instances[name] = self.table.options[name].value(self.table.master)
            self.instances[name].widget.add_listener(self)
            return self.instances[name]
        
    def GetData(self):
        """
        Gets the currently selected dropdown's values and passes it on as a dictionary.
        """
        return {str(self.table.options.__name__):self._checkInstance(self.table.chosenVal.get())}
    
    def _Set(self, key, value:dict):
        """
        when loading in last used values, populate the given widget's entries automatically.

        EXPECTED INPUT:
        key = E-Field, value = {'Fw': {'A': '0.2', 'B': '02'}}
        """
        method = ""
        params = None
        value = literal_eval(value)
        for k, v in value.items():
            method = k
            params = v
        # set the dropdown first
        #print(f'setting e field to: {method}')
        self.table._Set(key, method)
        if method == "Zero":
            return True
        # set the entries.
        for k, v in params.items():
            self._checkInstance(self.table.chosenVal.get()).Set(k, v)
        return True



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


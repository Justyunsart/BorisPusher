'''
Contains object-oriented GUI classes for general use.
Some are general, some are one time use.
'''

import tkinter as tk
from tkinter import ttk
from CurrentGuiClasses import *
from GuiHelpers import CSV_to_Df

# file stuff
from PrefFile import PrefFile
from pathlib import Path
import os
import pickle

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

            ## location of output folder
        outputPath = os.path.join(self.master.filepath, "Outputs")

        # 2: Create the PrefFile object with default params
        prefs = PrefFile(particlePath, 
                         coilPath, 
                         outputPath,
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

    def __init__(self, master, **kwargs):
        self.master = master
        # number 1: know the PATH of the program's root.
        self.filepath = str(Path(__file__).resolve().parents[1]) #Expected: '/BorisPusher/...'

        super().__init__(**kwargs)
        
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

class FileDropdown(ttk.Combobox):
    '''
    Stuff for when you want to change the input files. Instead of searching via
    the file explorer, this will initialize with all the files in the preferences' input DIRs
    in a dropdown menu.


    last = index of the last used file. Defaults to 0 unless overridden.
    '''
    dir:str # path to the folder you want to make its contents a dropdown menu of
    fileName:tk.StringVar

    PATH:Data #the full path to the file.

    def __init__(self, master, dir, last=0, **kwargs):
        self.master = master
        self.dir = dir
        self.fileName = tk.StringVar()
        self.PATH = Data('PATH')

         # check: make sure the dir exists. if not, create the dir.
        os.makedirs(dir, exist_ok=True)

        self.dir_contents = self._DIR_to_List()
        #print(self.dir_contents)

        super().__init__(master=master, values=self.dir_contents, textvariable=self.fileName, **kwargs)
        super().current(last)
        self._UpdatePath()

        # also add a trace to update all the field variables when it happens
        self.fileName.trace_add("write", self._UpdatePath)
    
    def _DIR_to_List(self):
        files = []
        for file in os.listdir(self.dir):
            path = os.path.join(self.dir, file)
            if os.path.isfile(path):
                files.append(file)
        if (files == []):
            files.append("")
        return files
    
    def _UpdatePath(self, *args):
        '''
        there's probably a built in way to do this but oh well.
        '''
        #print("updating path to: ", self.fileName.get())
        self.PATH.data = os.path.join(self.dir, self.fileName.get())

class LabeledEntry():
    '''
    An entry widget accompanied by a label widget on its left.
    '''
    value:tk.StringVar

    def __init__(self, master, val, row, col=0, title="title", **kwargs):
        self.master = master
        self.title = title
        self.value = tk.StringVar(value=val)

        self.label = tk.Label(self.master,
                              text=self.title,
                              justify="left")
        self.label.grid(row=row, column=col, columnspan=2, sticky="W")

        self.entry = tk.Entry(self.master,
                              textvariable=self.value,
                              **kwargs)
        self.entry.grid(row=row, column=col+2, columnspan=2, sticky="W")

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

    def __init__(self, master):
        self.master = master

        self.frame = tk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="W")
        self.master.grid_columnconfigure(0, weight=1)

        self.dt = LabeledEntry(self.frame, val=0.0000001, row=1, title="Timestep (sec): ", width = 10)
        self.dt.value.trace_add("write", self._Total_Sim_Time)
        
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
    
    def SaveData(self, dir: str):
        super().SaveData(dir)

        # In addition to the super, also update the selected file's value in the field dropdown
        if self.saveEntryVal.get() not in self.fileWidget["values"]:
            self.fileWidget["values"] += (self.saveEntryVal.get(),)
            self.fileWidget.current(len(self.fileWidget["values"]) - 1)
    
    def GetData(self):
        out =  super().GetData()
        out["Partile File"] = self.fileWidget.fileName.get()

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

class CoordTable(tk.LabelFrame):
    '''
    Diffrerent than an entry table (which has variable field types).
    Here, the table is hard set to 3 entries - X, Y, and Z.

    Used for setting the B and E fields, for example.

    I made this a new class because its usecase is different enough for it to not use many of Entrytable's
    functions.
    '''
    def __init__(self, master, title= "coords", **kwargs):
        self.master = master
        self.title = title
        super().__init__(master, text = self.title, **kwargs)

        #frame for the entry widgets
        self.frame1 = tk.Frame(self)
        self.frame1.grid(row=1, column=0)

        self.X = LabeledEntry(self.frame1, 0, row=1, col=0, title="X: ", width=10)
        self.Y = LabeledEntry(self.frame1, 0, row=1, col=4, title="Y: ", width=10)
        self.Z = LabeledEntry(self.frame1, 0, row=1, col=8, title="Z: ", width=10)
        self.entries = [self.X.entry, self.Y.entry, self.Z.entry] # handy reference to all entry widgets

        # frame for the use checkmark
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="W")

        self.doUse = tk.IntVar(value = 0)  #using a var makes value tracking easier.

        self.calcCheck = tk.Checkbutton(self.frame, variable= self.doUse, text="Use?")
        self.calcCheck.grid(row=0, column=0, sticky="W")

        self.doUse.trace_add("write", self.CheckEditability)

        self.CheckEditability() # set the entries in their correct state.

    def GetData(self):
        '''
        when asked, will return the captured coordinates as a list.
        '''
        out = {}
        keyName = self.title
        keyUse = f'{keyName}_Use'
        value = [float(self.X.entry.get()), float(self.Y.entry.get()), float(self.Z.entry.get())]
        
        out[keyName] = value
        out[keyUse] = self.doUse.get() # so the program knows whether to use these static field vals or not.

        return out

    def CheckEditability(self, *args, **kwargs):
        '''
        used when self.calcCheck is toggled on; makes these cells in an editable state
        '''
        useState = self.doUse.get()

        if(useState == 0):
            '''
            useState is off: all entries should be read-only.
            '''
            #print("disable")
            for entry in self.entries:
                entry.config(state="disabled")
        else:
            '''
            entries are otherwise editable.
            '''
            for entry in self.entries:
                entry.config(state="normal")

class CoilButtons():
    '''
    helpful autofill widgets for stuff like:
        > quick setups for mirror, hexahedron

    
    This will sit next to the entry table, and will feature buttons and entries.
    '''
    def __init__(self, master):
        self.master = master

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
                                width=10)
        self.dia = LabeledEntry(master=entryFrame,
                                row=1,
                                col=0,
                                title="Diameter: ",
                                val=0.,
                                width=10)
        self.amp = LabeledEntry(master=entryFrame,
                                row=2,
                                col=0,
                                title="Current: ",
                                val=0.,
                                width=10)
        
        ### Button to apply changes - on its own frame for ease of gridding
        buttonFrame = tk.Frame(master=paramFrame)
        buttonFrame.grid(row=4, column=0, pady=10)
        self.apply = tk.Button(master = buttonFrame,
                               text="Apply")
        self.apply.grid(row=0, column=0, sticky= "")
        


class CurrentConfig:
    def __init__(self, master, DIR):
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

        CurrentGraph = tk.Frame(self.master)
        CurrentGraph.grid(row=1, column=0)
        
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
                            graphFrame=CurrentGraph)
        
        self.param = CoilButtons(ParamFrame)


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


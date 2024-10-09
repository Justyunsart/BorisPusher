'''
Contains object-oriented GUI classes for general use.
Some are general, some are one time use.
'''

import tkinter as tk
from tkinter import ttk
from CurrentGuiClasses import EntryTable, file_particle
from GuiHelpers import CSV_to_Df


# file stuff
from PrefFile import PrefFile
from pathlib import Path
import os
import pickle
import pandas as pd

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

    PATH:str #the full path to the file.

    def __init__(self, master, dir, last=0, **kwargs):
        self.master = master
        self.dir = dir
        self.fileName = tk.StringVar()

        self.dir_contents = self._DIR_to_List()
        #print(self.dir_contents)

        super().__init__(master=master, values=self.dir_contents, textvariable=self.fileName, **kwargs)
        super().current(last)
        self.PATH = os.path.join(self.dir, self.fileName.get())
    
    def _DIR_to_List(self):
        files = []
        for file in os.listdir(self.dir):
            path = os.path.join(self.dir, file)
            if os.path.isfile(path):
                files.append(file)
        return files

class LabeledEntry():
    '''
    An entry widget accompanied by a label widget on its left.
    '''
    value:tk.StringVar

    def __init__(self, master, val, row, title="title", **kwargs):
        self.master = master
        self.title = title
        self.value = tk.StringVar(value=val)

        self.label = tk.Label(self.master,
                              text=self.title,
                              justify="left")
        self.label.grid(row=row, column=0, columnspan=2, sticky="W")

        self.entry = tk.Entry(self.master,
                              textvariable=self.value,
                              **kwargs)
        self.entry.grid(row=row, column=2, columnspan=2, sticky="W")

class Particle_File_Dropdown(FileDropdown):
    def __init__(self, master, dir, last=0, **kwargs):
        self.master = master

        self.frame = tk.Frame(master=self.master)
        self.frame.grid(row=0, column=0)

        super().__init__(self.frame, dir, last, **kwargs)
        super().grid(row=0, column=1)

        self.label = tk.Label(self.frame,
                              text="Particle Conditions: ")
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

class ParticlePreview(EntryTable):
    '''
    An entrytable for viewing and editing particle initial condition csvs.
    '''
    def __init__(self, master, fileWidget, dataclass=file_particle):
        self.fileWidget = fileWidget
        super().__init__(master, dataclass)
        self.Read_Data()
    
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
        data = CSV_to_Df(self.fileWidget.PATH).values.tolist() # ideally, each sublist will be a row of params for file_particle
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
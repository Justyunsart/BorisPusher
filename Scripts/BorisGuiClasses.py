'''
Contains object-oriented GUI classes for general use.
'''

import tkinter as tk
from tkinter import ttk

# file stuff
from PrefFile import PrefFile
from pathlib import Path
import os
import pickle

class ConfigMenuBar():
    def __init__ (self, master):
        self.master = master

        self.InitUI()

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

        # 2: Create the PrefFile object
        prefs = PrefFile(particlePath, coilPath, outputPath)
     
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

    def __init__(self, master, **kwargs):
        self.master = master
        # number 1: know the PATH of the program's root.
        self.filepath = str(Path(__file__).resolve().parents[1]) #Expected: '/BorisPusher/...'

        super().__init__(**kwargs)
        
        self._Init_Configs()

    #=============#
    # CONFIG INIT #
    #=============#
    def _Init_Configs(self):
        '''
        On application start, populate simulation configurations.

        
        Stuff like, all available restart files, coil configurations, 
        as well as last used configs.
        (Just get the DIR where these are stored)
        '''

class FileDropdown(ttk.Combobox):
    '''
    Stuff for when you want to change the input files. Instead of searching via
    the file explorer, this will initialize with all the files in the preferences' input DIRs
    in a dropdown menu.


    last = index of the last used file. Defaults to 0 unless overridden.
    '''
    dir:str # path to the folder you want to make its contents a dropdown menu of

    def __init__(self, master, dir, last=0, **kwargs):
        self.master = master
        self.dir = dir

        self.dir_contents = self._DIR_to_List()

        super().__init__(master=master, values=[self.dir_contents],**kwargs)
        self.current(last)
    
    def _DIR_to_List(self):
        files = []
        for file in os.listdir(self.dir):
            if os.path.isfile(file):
                files.append(file)
        return files


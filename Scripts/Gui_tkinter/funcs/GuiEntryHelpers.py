from system.Observer import Data
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, field
import csv
from ast import literal_eval
import numpy as np
import os
import shutil
import ast
import pandas as pd
from settings.palettes import Drapion
import math
import magpylib as mp
from pathlib import Path
from magpylib.current import Circle

"""
classes used for <CurrentGuiClasses.EntryTable> and its subclasses.


stored in its own file to ensure that all of these classes are loaded 
before any entrytable is constructed.
"""
class Dropdown(tk.Frame):
    """
    creates a dropdown with all the options being defined by the provided options list.
    """
    chosenVal: tk.StringVar
    def __init__(self, master, options:list, label="New Dropdown: ", default:int=0):
        super().__init__(master)
        self.grid(row=0, column=0)
        self.chosenVal = tk.StringVar()
        self.master = master
        label = tk.Label(self,
                         text=label)
        label.grid(row=0, column=0)

        # dropdown and its values
        self.dropdown = ttk.Combobox(self,
                                     textvariable=self.chosenVal,
                                     state="readonly")
        self.dropdown.grid(row=0, column=1)
        self.dropdown['values'] = tuple(options)
        self.dropdown.current(default)


class CoordTable(tk.LabelFrame):
    '''
    Diffrerent than an entry table (which has variable field types).
    Here, the table is hard set to 3 entries - X, Y, and Z.

    Used for setting the B and E fields, for example.

    I made this a new class because its usecase is different enough for it to not use many of Entrytable's
    functions.
    '''
    listeners:list
    def __init__(self, master, title= "coords", doInit=True, **kwargs):
        self.listeners = []
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
        self.labeledEntries = [self.X, self.Y, self.Z]

        # frame for the use checkmark
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="W")

        self.doUse = tk.IntVar(value = 0)  #using a var makes value tracking easier.

        self.calcCheck = tk.Checkbutton(self.frame, variable= self.doUse, text="Use?")
        self.calcCheck.grid(row=0, column=0, sticky="W")

        self.doUse.trace_add("write", self.CheckEditability)

        if(doInit):
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
    
    def SetCheck(self, val):
        self.doUse.set(val)
    def SetCoords(self, val):
        val = ast.literal_eval(val)
        #val = [n.strip() for n in val]
        for i in range(3):
            self.labeledEntries[i].value.set(val[i])
    def add_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)
    def trigger_listener(self, *args):
        for listener in self.listeners:
            listener.update()

# MORE GENERIC CLASSES #
#==============================================================
def GetAxis(coord):
    index_max = np.argmax(coord)
    return index_max

def tryEval(val):
    try:
        #print(val)
        return literal_eval(val)
    except ValueError:
        """
        Will only handle cases where the string contains multiplied floats.
        """
        if '*' in val:
            temp = val.split('*')
            temp = list(map(float, temp))
            out = math.prod(temp)
            return out
        else:
            return val

class FileDropdown(tk.Frame):
    '''
    TLDR: DROPDOWN w/ FILES FROM GIVEN DIR. 
    Stuff for when you want to change the input files. Instead of searching via
    the file explorer, this will initialize with all the files in the preferences' input DIRs
    in a dropdown menu.


    last = index of the last used file. Defaults to 0 unless overridden.
    '''
    #fileName:tk.StringVar

    #PATH:Data #the full path to the file.

    def __init__(self, master, dir, last=0, default:callable=None, **kwargs):
        self.master = master # parent frame.
        self.last = last
        self.default_name = "New_File"
        self.default_callable = default # function to generate a default file (if the provided DIR is empty.)

        # initialize the frame to populate w/ label and combobox.
        # the class inherits from tk.Frame so I can control packing when I instantiate it.
        super().__init__(master=master)

        # aesthetics vars
        self.label = tk.Label(self, text="File: ")

        # dropdown tracking vars
        self.dir = dir
        dir.path.attach(self) # add ref so you know when to call updates.
        self.fileName = tk.StringVar()
        self.PATH = Data('PATH')

        self.update(self.dir.path.data, **kwargs)

        # PACKING
        self.label.pack(side='left')
        self.combo_box.pack(side='left')

    """
    Called when the 'dir' parameter notifies the need for an update.
    value = the path to read.
    """
    def update(self, value, **kwargs):
        #print(f"Gui_tkinter.funcs.GuiEntryHelpers.FileDropdown.update: {value}")
        # check: make sure the dir exists. if not, create the dir.
        os.makedirs(value, exist_ok=True)
        self.dir_contents = self._DIR_to_List()

        # initialize the combobox
        self.combo_box = ttk.Combobox(master=self, values=self.dir_contents, textvariable=self.fileName, state='readonly', **kwargs)
        try:
            self.combo_box.current(self.last)
        except tk.TclError:
            self.default_callable()
        self._UpdatePath()

        # also add a trace to update all the field variables when it happens
        self.fileName.trace_add("write", self._UpdatePath)


    def _DIR_to_List(self):
        files = [] # the final output list 
        # filter the dir to get the list of files only.
        _files = [f for f in os.listdir(self.dir.path.data) if os.path.isfile(os.path.join(self.dir.path.data, f)) and not (f[0] == '.')]
        if len(_files) == 0:
            self.create_default()
            _files = os.listdir(self.dir.path.data)

        for file in _files:
            path = os.path.join(self.dir.path.data, file)
            if os.path.isfile(path):
                files.append(file)
        return files
    
    def create_default(self, *args):
        """
        Run whenever there are no files in the current directory that is being read.
        If the default attribute is not None, then that file is created.
        """
        if self.default_callable is not None:
            # run the provided function if it's not None
            self.default_callable(self.dir.path.data)

    def _UpdatePath(self, *args):
        '''
        callback to update the full path to the edited file.
        '''
        #print("updating path to: ", self.fileName.get())
        self.PATH.data = os.path.join(self.dir.path.data, self.fileName.get())

class LabeledEntry():
    '''
    An entry widget accompanied by a label widget on its left.
    '''
    value:tk.StringVar

    def __init__(self, master, val, row, col=0, col_span=2, title="title", **kwargs):
        self.master = master
        self.title = title
        self.value = tk.StringVar(value=val)

        self.label = tk.Label(self.master,
                              text=self.title,
                              justify="left")
        self.label.grid(row=row, column=col, columnspan=col_span, sticky="W")

        self.entry = tk.Entry(self.master,
                              textvariable=self.value,
                              **kwargs)
        self.entry.grid(row=row, column=col + col_span, columnspan=col_span, sticky="E")
    
    def toggle(self, state:str):
        """
        state: 'on' or 'off'

        Renders the widget visible or invisible. Does not destroy widget.
        """
        match state:
            case 'on':
                self.label.grid()
                self.entry.grid()
            case 'off':
                self.label.grid_remove()
                self.entry.grid_remove()

class OnlyNumEntry(tk.Entry):
    # normal look of the entry widget.
    normal_style = {"highlightcolor":Drapion.Entry_Table_Cell_Highlight.value,
                    "highlightbackground":Drapion.Transparent_Highlight_Bg.value}
    
    # applied whenever there is a problem to notify the user abt. 
    warning_style = {"highlightcolor":Drapion.Warning_Highlight.value,
                     'highlightbackground':Drapion.Warning_Highlight.value}

    def __init__(self, master, **kwargs):
        self.is_warned = False # attribute that keeps track of the widget's current state.
        # other initialization
        self.var = tk.StringVar(master=master)
        self.isNum = False
        super().__init__(master, textvariable=self.var, width=10, **kwargs, **self.normal_style)
        #print(self.cget('highlightbackground'))

        # event handling - make sure this class is included in bindtags
        btags = list(self.bindtags())

        btagInd = btags.index("Entry") + 1 # make this class's events go after the base class, so that we're working with the updated values
        btags.insert(btagInd, "OnlyNumEntry")
        self.bindtags(tuple(btags))

        # add trace
        self.var.trace_add('write', self.validate)

    def trigger_warning(self):
        """
        changes the widget's style to warning_style.
        """
        # do nothing if the widget is already in the warned state
        self.configure(**self.warning_style) if not self.is_warned else None
        self.is_warned = True
        #print("warned")
    
    def untrigger_warning(self):
        """
        changes the widget's style back to the normal style.
        """
        # do nothing if the widget is already in the normal state
        self.configure(**self.normal_style) if self.is_warned else None
        self.is_warned = False
        #print("unwarned")

    def validate(self, *args):
        try:
            float(self.var.get())
            self.isNum = True
        except:
            self.isNum = False

class EntryButton(tk.Button):
    def __init__(self, master, **kwargs):
        self.master = master
        super().__init__(master, **kwargs)
    def get(self):
        return self


class EntryTableParam:
    paramDefault: None
    paramWidget: callable

    def __init__(self, default, master, widget=OnlyNumEntry, **kwargs):
        self.paramDefault = default
        self.paramWidget = widget(master, **kwargs)
        self._SetDefault()
    
    def _SetDefault(self):
        """
        Sees the type of the widget the object is created with, and populates it with default value with the provided paramDegault peoperty.
        NOTE: tk.Combobox objects are assumed to be for rotations only, and are populated with 'x', 'y', and 'z'.
        """
        match self.paramWidget:
            case OnlyNumEntry():
                self.paramWidget.insert(0, self.paramDefault)
            case ttk.Combobox():
                self.paramWidget["values"] = ["x",
                                              "y",
                                              "z"]
                self.paramWidget.current(self.paramDefault)
            case tk.Button():
                pass

    def get(self, isNum=False):
        if isNum:
            return float(self.paramWidget.get())
        else:
            return self.paramWidget.get()

"""
Helper function to read csv data to a magpylib.Collection object
"""
def File_to_Collection(path, filename='coils.txt', converters={}, read_file=True):
    """
     1. locate the coils file, assuming that path is the dir. to the json.
     2. return the coils as a magpy collection object.
    """
    c = mp.Collection()
    if read_file:
        proot = str(Path(path).parents[0])  # boris_<nsteps>_<simtime>_<nparts>
        # print(f"{path}, {root}")
        coilpath = os.path.join(proot, filename)  # boris_<nsteps>_<simtime>_<nparts>/coils.txt

        # in case the output folder does not have a coils.txt file.
        if (not os.path.exists(coilpath)):
            return c  # return an empty collection

        # store coils and rotations separately, so that we can apply the rotations afterwards
        df = CSV_to_Df(coilpath, converters=converters,
                       isNum=False, header=0)
    else:
        df = path
    # print(df)
    for i, row in df.iterrows():
        row = row.tolist()
        position = [float(row[0]), float(row[1]), float(row[2])]
        # print(tryEval(row[6]))
        coil = Circle(position, current=float(row[3]), diameter=float(row[4]))
        # print(coil)
        match row[5]:
            case float():
                coil.rotate_from_angax(row[5], row[6])
            case int():
                coil.rotate_from_angax(row[5], row[6])
            case list():
                for i in range(len(row[5])):
                    coil.rotate_from_angax(float(row[5][i]), row[6][i])

        c.add(coil)
    return c



def CSV_to_Df(dir, isNum=True, **kwargs):
    '''
    A function that will be called in the calculate button's command.
    Turns the csv data in the particle input file to a workable dataframe.

    dir: path to the file to be read.
    isNum: a bool that determines if everything should be considered numeric or not.
    '''
    # step 1: read the file from the directory.
    data = pd.read_csv(dir, **kwargs)

    if data.empty:
        data = pd.read_json(dir, orient="table")
    #print(data)

    # step 2: numeric checks
    ## does not iterate if the entire df is numeric.
    if (isNum):
        data.apply(pd.to_numeric)
    ## iterates through columns if the entire dataframe is not numeric.
    else:
        for col in data:
            try:
                data[col] = data[col].astype(float)
            except ValueError:
                pass
    #print(data)
    return data


def List_to_CSV(fileName, data, *args, **kwargs):
    '''
    turns an input of a nested list to a csv text file
    '''
    #print(data)
    with open(fileName, "w", *args, **kwargs) as mycsv:
        writer = csv.writer(mycsv)
        writer.writerows(data)

def Dict_to_CSV(fileName:str, data:dict, *args, **kwargs):
    """
    used to create the last used parameters file.
    """
    with open(fileName, "w", *args, **kwargs) as mycsv:
        writer = csv.DictWriter(mycsv, data.keys())
        writer.writeheader()
        writer.writerow(data)

def JSON_to_Df(path, orient="table", numeric=True):
    """
    reads a json file from the supplied path and returns it as a numeric table.
    """
    df = pd.read_json(path, orient=orient)

    if(numeric):
        df = df.apply(pd.to_numeric)
    return df

"""
DATACLASSES USED FOR THE ENTRY TABLES.

The entry table class knows the column number, name, and widget type to populate with these dataclasses.
    > It had to be done like this so some columns can be programmed to spawn buttons instead of a tk.Entry.
"""


@dataclass
class Bob_e_Config_Dataclass():
    '''
    For circles in the bob_e method, the relevant params are:
        - position
        - rotation
        - diameter
    '''
    PosX: EntryTableParam = field(init=False)
    PosY: EntryTableParam = field(init=False)
    PosZ: EntryTableParam = field(init=False)

    Q: EntryTableParam = field(init=False)
    Diameter: EntryTableParam = field(init=False)

    Rotations: EntryTableParam = field(init=False)

    eval_inds = (5, 6) # index reference of the rotation_angles and rotation_axes lists
    power_name = "Q"

    def __init__(self, frame, PosX = 0, PosY = 0, PosZ = 0, Q = 1e5, Diameter = 1, RotationAngle = [], RotationAxis = [], **kwargs):
        self.PosX = EntryTableParam(PosX, master=frame)
        self.PosY = EntryTableParam(PosY, master=frame)
        self.PosZ = EntryTableParam(PosZ, master=frame)

        self.Q = EntryTableParam(Q, master=frame)
        self.Diameter = EntryTableParam(Diameter, master=frame)

        self.Rotations = EntryTableParam(None, widget=EntryButton, master=frame, text="Rotations")

        self.iterables = [self.PosX, self.PosY, self.PosZ, self.Q, self.Diameter, self.Rotations]

        # properties that are useful, and are hidden from iteration.
        self.rotation_angles = RotationAngle
        self.rotation_axes = RotationAxis


    @property
    def rotation_angles(self):
        return self._rotation_angles
    @rotation_angles.setter
    def rotation_angles(self, val):
        try:
            val = ast.literal_eval(val)
        except ValueError:
            pass
        assert type(val) == list
        self._rotation_angles = val

    @property
    def rotation_axes(self):
        return self._rotation_axes
    @rotation_axes.setter
    def rotation_axes(self, val):
        try:
            val = ast.literal_eval(val)
        except ValueError:
            pass
        assert type(val) == list
        self._rotation_axes = val
    
    def __iter__(self):
        for val in self.iterables:
            yield val
    
    def get_dict(self, to_csv=False):
        """
        returns all attributes from the self.iterables list as a dictionary.
        The keys are the attribute names, and the values are, their values lol.
        """
        if(not to_csv):
            out = {key:value.get() for key, value in vars(self).items() if value in self.iterables}
            out['Rotations'] = {"Angles" : self.rotation_angles, "Axes" : self.rotation_axes}
        else:
            out = {key:[value.get()] for key, value in vars(self).items() if value in self.iterables}
            out['RotationAngle'] = [self.rotation_angles]
            out['RotationAxis'] = [self.rotation_axes]
            del out['Rotations']
        return out

@dataclass
class Disk_e_Config_Dataclass(Bob_e_Config_Dataclass):
    Inner_r: EntryTableParam = field(init=False)

    def __init__(self, frame, PosX = 0, PosY = 0, PosZ = 0, Q=0.00000000001, Diameter = 1, RotationAngle = [], RotationAxis = [], Inner_r=0.5):
        super().__init__(frame=frame, PosX=PosX, PosY=PosY, PosZ=PosZ, Q=Q, Diameter=Diameter, RotationAngle=RotationAngle, RotationAxis=RotationAxis)
        self.Inner_r = EntryTableParam(Inner_r, master=frame)
        self.iterables.append(self.Inner_r)

@dataclass
class RotationConfig():
    '''
    when clicking on the current config's rotations button, it will open a new window containing the rotation transformations
    of the row.
    '''
    RotationAngle: EntryTableParam = field(init=False)
    RotationAxis: EntryTableParam = field(init=False)

    def __init__ (self, frame, angle=0, axis=0):
        self.RotationAngle = EntryTableParam(angle, master=frame)
        self.RotationAxis = EntryTableParam(axis, widget=ttk.Combobox, master=frame, state="readonly", width=5)
        self.iterables = [self.RotationAngle, self.RotationAxis]
    def __iter__(self):
        for val in self.iterables:
            yield val
    def get_dict(self, csv=False):
        """
        returns all attributes from the self.iterables list as a dictionary.
        The keys are the attribute names, and the values are, their values lol.
        """
        # the csv parameter is abstracted across several dataclasses. It isn't used in this one, so always have it be False for protection.
        # it wouldn't do anthing if it was passed with True in the first place haha.
        csv = False
        return {key:value.get() for key, value in vars(self).items() if value in self.iterables}

@dataclass
class CircleCurrentConfig():
    '''
    An object created from (I'm assuming) a 'create new current' button.
    Assume that this is like an entry object for a scrollbar table.
    '''
    PosX: EntryTableParam = field(init=False)
    PosY: EntryTableParam = field(init=False)
    PosZ: EntryTableParam = field(init=False)

    Amp: EntryTableParam = field(init=False)
    Diameter: EntryTableParam = field(init=False)

    Rotations: EntryTableParam = field(init=False)
    # we need this index so we know to run ast.literal_eval on these indices.
    eval_inds = (5, 6) # index reference of the rotation_angles and rotation_axes lists
    power_name = "Amp"

    def __init__(self, frame, PosX = 0, PosY = 0, PosZ = 0, Amp = 1e5, Diameter = 1, RotationAngle = [], RotationAxis = []):
        self.PosX = EntryTableParam(PosX, master=frame)
        self.PosY = EntryTableParam(PosY, master=frame)
        self.PosZ = EntryTableParam(PosZ, master=frame)

        self.Amp = EntryTableParam(Amp, master=frame)
        self.Diameter = EntryTableParam(Diameter, master=frame)

        self.Rotations = EntryTableParam(None, widget=EntryButton, master=frame, text="Rotations")
        
        self.iterables = [self.PosX, self.PosY, self.PosZ, self.Amp, self.Diameter, self.Rotations]

        # properties that are useful, and are hidden from iteration.
        self._rotation_angles = RotationAngle
        self._rotation_axes = RotationAxis

    @property
    def rotation_angles(self):
        return self._rotation_angles
    @rotation_angles.setter
    def rotation_angles(self, val):
        try:
            val = ast.literal_eval(val)
        except ValueError:
            pass
        assert type(val) == list
        self._rotation_angles = val

    @property
    def rotation_axes(self):
        return self._rotation_axes
    @rotation_axes.setter
    def rotation_axes(self, val):
        try:
            val = ast.literal_eval(val)
        except ValueError:
            pass
        assert type(val) == list
        self._rotation_axes = val

    def __iter__(self):
        for val in self.iterables:
            yield val

    def get_dict(self, to_csv=False):
        """
        returns all attributes from the self.iterables list as a dictionary.
        The keys are the attribute names, and the values are, their values lol.
        """
        if(not to_csv):
            out = {key:value.get() for key, value in vars(self).items() if value in self.iterables}
            out['Rotations'] = {"Angles" : self.rotation_angles, "Axes" : self.rotation_axes}
        else:
            out = {key:[value.get()] for key, value in vars(self).items() if value in self.iterables}
            out['RotationAngle'] = [self.rotation_angles]
            out['RotationAxis'] = [self.rotation_axes]
            del out['Rotations']
        return out

@dataclass
class file_particle:
    '''
    dataclass for particles, only used for the csv config files.
    '''
    #position
    px: EntryTableParam = field(init=False)
    py: EntryTableParam = field(init=False)
    pz: EntryTableParam = field(init=False)

    # Velocity
    vx: EntryTableParam = field(init=False)
    vy: EntryTableParam = field(init=False)
    vz: EntryTableParam = field(init=False)

    def __init__ (self, frame, px=0., py=0., pz=0., 
                  vx=0., vy=0, vz=0):
        self.px = EntryTableParam(px, master=frame)
        self.py = EntryTableParam(py, master=frame)
        self.pz = EntryTableParam(pz, master=frame)
        
        self.vx = EntryTableParam(vx, master=frame)
        self.vy = EntryTableParam(vy, master=frame)
        self.vz = EntryTableParam(vz, master=frame)

        self.iterables = [self.px, self.py, self.pz, self.vx, self.vy, self.vz]

    
    def __iter__(self):
        for val in self.iterables:
            yield val
    
    def get_dict(self, to_csv=False):
        """
        returns all attributes from the self.iterables list as a dictionary.
        The keys are the attribute names, and the values are, their values lol.
        """
        if to_csv:
            out = {key: [value.get()] for key, value in vars(self).items() if value in self.iterables}
        else:
            out = {key:value.get() for key, value in vars(self).items() if value in self.iterables}
        return out
    
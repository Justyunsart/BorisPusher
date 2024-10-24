import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, field
import csv
from ast import literal_eval

"""
classes used for <CurrentGuiClasses.EntryTable> and its subclasses.


stored in its own file to ensure that all of these classes are loaded 
before any entrytable is constructed.
"""
# MORE GENERIC CLASSES #
#==============================================================
def tryEval(val):
    try:
        return literal_eval(val)
    except (ValueError, SyntaxError):
        return val


class OnlyNumEntry(tk.Entry, object):
    def __init__(self, master, **kwargs):

        # other initialization
        self.var = tk.StringVar(master)
        self.isNum = False
        tk.Entry.__init__(self, master, textvariable=self.var, width=10, **kwargs)

        # event handling - make sure this class is included in bindtags
        btags = list(self.bindtags())

        btagInd = btags.index("Entry") + 1 # make this class's events go after the base class, so that we're working with the updated values
        btags.insert(btagInd, "OnlyNumEntry")
        self.bindtags(tuple(btags))

        # add trace
        self.var.trace_add('write', self.validate)

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

    def __init__(self, default, widget=OnlyNumEntry, **kwargs):
        self.paramDefault = default
        #print (self.paramDefault)
        self.paramWidget = widget(**kwargs)
        self._SetDefault()
    
    def _SetDefault(self):
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

    def Get(self, isNum=True):
        if isNum:
            return float(self.paramWidget.get())
        else:
            return self.paramWidget.get()


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
        self.RotationAxis = EntryTableParam(axis, ttk.Combobox, master=frame, state="readonly", width=5)
    def __iter__(self):
        for val in self.__dict__.values():
            yield val

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
    #RotationAngle: EntryTableParam = field(init=False)
    #RotationAxis: EntryTableParam = field(init=False)

    def __init__(self, frame, px = 0, py = 0, pz = 0, amp = 1e5, dia = 1):
        self.PosX = EntryTableParam(px, master=frame)
        self.PosY = EntryTableParam(py, master=frame)
        self.PosZ = EntryTableParam(pz, master=frame)

        self.Amp = EntryTableParam(amp, master=frame)
        self.Diameter = EntryTableParam(dia, master=frame)

        self.Rotations = EntryTableParam(None, EntryButton, master=frame, text="Rotations")
        #self.RotationAngle = EntryTableParam(angle, master=frame)
        #self.RotationAxis = EntryTableParam(axis, ttk.Combobox, master=frame, state="readonly", width=5)
        
    def __iter__(self):
        for val in self.__dict__.values():
            yield val


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
    
    def __iter__(self):
        for val in self.__dict__.values():
            yield val
    
class Observed:
    '''
    A value that is being watched for any changes.
    
    
    Event subscribers will run their update function
    upon being notified.
    '''
    def __init__ (self):
        self._observers = []
    
    def notify (self, modifier = None):
        '''
        Run update function in observers
        '''
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)
    
    def attach(self, observer):
        '''
        Add observer to list if not in list already
        '''
        if observer not in self._observers:
            self._observers.append(observer)
        
    def detach(self, observer):
        '''
        if in list, remove observer
        '''
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

class Data(Observed):
    '''
    thing that is being observed, with initilizer data and such
    '''
    def __init__ (self, name=''):
        Observed.__init__(self)
        self.name = name
        self._data = 0
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value
        self.notify()
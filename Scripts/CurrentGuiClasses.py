'''
Another GUI script. This time, this script creates a base class for current configurations in the GUI.
Users will basically create instances of this to customize the current.

It's basically a container for parameters to create magpylib objects
'''

import tkinter as tk
from dataclasses import dataclass, asdict

class EntryTable:
    '''
    A generic class for tables that allow user generated and deleted entries.
    Basically a fun csv editor.
    
    # PARAMETERS
    master: you need to pass the master tkinter object this belongs to. Either a root or toplevel object.

    dataclass: the variables the table needs to represent.
    '''
    #========#
    # FIELDS #
    #========#

    # info from the supplied dataclass.
    numcols: int
    fields: list

    # metadata
    entries: list
    data: dataclass

    #===============#
    # INITIALIZAION #
    #===============#
    def __init__(self, master, dataclass:dataclass): # initialization function
        # keep reference to the master 
        self.master = master
        self.entries = []

        # read the fields from the supplied dataclass.
        self.data = dataclass
        self.fields = list(dataclass.__dataclass_fields__.keys())
        self.fieldDefaults = list(dataclass.__dataclass_fields__.values())
        self.numcols = len(self.fields)


        #---------#
        # WIDGETS #
        #---------#
        self.frame = tk.LabelFrame(self.master,
                                   text="EntryTable")
        self.frame.grid(row=0, column=0)
        self.frame1 = tk.Frame(self.frame) # frame for table data
        self.frame1.grid(row=0, column=0)
        
        for i in range(self.numcols): # create top row of the data table
            self.titleLabel = tk.Label(self.frame1,
                                       text=str(self.fields[i]))
            self.titleLabel.grid(row=0, column=i)
        self.NewEntry() # add one empty row for the start

        self.addButton = tk.Button(self.frame,
                                   text="New Entry",
                                   command=self.NewEntry)
        self.addButton.grid(row=1, column=0)
    
    #===========#
    # CALLBACKS #
    #===========#
    def NewEntry(self):
        entry = self.data()
        defvals = list(asdict(entry).values())
        self.entries.append(entry)
        for i in range(self.numcols):
            self.entry = tk.Entry(self.frame1)
            self.entry.insert(0, defvals[i])
            self.entry.grid(row = len(self.entries)+1, column=i)

class CurrentGraphWidget:
    '''
    ideally, this should automatically graph proposed, valid current configurations in the entry table.
    '''
    def __init__(self, master):
        self.master = master



@dataclass
class CircleCurrentConfig:
    '''
    An object created from (I'm assuming) a 'create new current' button.
    Assume that this is like an entry object for a scrollbar table.
    '''
    PosX: float = 0.
    PosY: float = 0.
    PosZ: float = 0.

    Amp: float = 1e5
    Diameter: float = 1.

    RotationX: float = 0.
    RotationY: float = 0.
    RotationZ: float = 0.


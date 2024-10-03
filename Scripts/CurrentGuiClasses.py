'''
Another GUI script. This time, this script creates a base class for current configurations in the GUI.
Users will basically create instances of this to customize the current.

It's basically a container for parameters to create magpylib objects
'''

import tkinter as tk
from dataclasses import dataclass, asdict
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from functools import partial

from magpylib import show
from magpylib import Collection
from magpylib.current import Circle

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

    # FIELD GETTERS
    def GetEntries(self):
        return self.entries
    
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
        # PARENT FRAME FOR ALL CONTENTS
        self.frame = tk.LabelFrame(self.master,
                                   text="EntryTable")
        self.frame.grid(row=0, column=0)

        # frame for table data
        self.frame1 = tk.Frame(self.frame) 
        self.frame1.grid(row=0, column=0)

        # create top row of the data table (name of vars)
        for i in range(self.numcols): 
            self.titleLabel = tk.Label(self.frame1,
                                       text=str(self.fields[i]))
            self.titleLabel.grid(row=0, column=i)
        self.NewEntry() # add one empty row for the start

        # Button to add new rows
        self.addButton = tk.Button(self.frame,
                                   text="New Entry",
                                   command=self.NewEntry)
        self.addButton.grid(row=1, column=0)
    
    #===========#
    # CALLBACKS #
    #===========#
    
    def EntryValidateCallback(self, entry):
        '''
        Callback function that is called by entryboxes.

        When a user updates an entry box, call this function to:
            1. Validate entry type (not implemented here atm)
            2. Update its corresponding field in self.entries
        '''

        # To get the corresponding index and field in self.entries, we need to first extract the grid position of the entry box.

        # Row index = self.entry index
        # Column index = field index
        info = entry.grid_info()
        rowInd = info["row"] - 1    # minus one to account for the first row being titles, var names
        colInd = info["column"]

        # Now we extract the newly edited value to allow for examination.
        entryValue = entry.get()
        print(self.GetEntries(), rowInd, colInd, entryValue)
        
        if(entry.isNum):
            self.GetEntries()[rowInd].__setattr__(self.fields[colInd], float(entryValue))
            print(self.GetEntries()[rowInd])
        return True

    def NewEntry(self):
        '''
        Creates a new row for the entry table
        '''
        entry = self.data()
        defvals = list(asdict(entry).values())
        self.GetEntries().append(entry)

        for i in range(self.numcols):
            # create the respective entry box
            self.entry = OnlyNumEntry(self.frame1,
                                  validate="key")

            # populate entry with class default values
            self.entry.insert(0, defvals[i])
            self.entry.grid(row = len(self.entries), column=i)
            self.entry.config(validatecommand=
                              partial(self.EntryValidateCallback, entry=self.entry))
    


class CurrentEntryTable(EntryTable):
    '''
    The Entry Table for currents will have a (probably unique) graph button, so I made a subclass to extend that functionality.

    I'll probably also include the graph widget in this class for simplicity.
    '''
    def __init__(self, master, dataclass):
        super().__init__(master, dataclass)
        # Graph update button; can replace with validate callbacks later
        self.graphButton = tk.Button(self.frame,
                                     text="Graph",
                                     command=self.GraphCoils)
        self.graphButton.grid(row=1, column=1)

        # Frame for the graph: sits below the entry table
        self.frame2 = tk.LabelFrame(self.frame,
                                    text="Graph")
        self.frame2.grid(row=2, column=0)

        #--------#
        # FIGURE #
        #--------#
        self.fig = plt.figure(figsize=(10, 10))
        self.plot = self.fig.add_subplot(1,1,1, projection="3d")
        
        self.canvas = FigureCanvasTkAgg(self.fig,
                                        master = self.frame2)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)
    
    def GraphCoils(self):
        '''
        1. Extracts the data from self.entries
        2. Creates magpylib circle current objects from this data
        3. Graphs these created coils
        '''
        collection = Collection()
        for circle in self.GetEntries():
            pos = [circle.PosX, circle.PosY, circle.PosZ]
            c = Circle(current=circle.Amp,
                                   position=pos,
                                   diameter = circle.Diameter
                                   )
            c.rotate_from_angax(circle.RotationAngle, circle.RotationAxis)
            collection.add(c)
        
        show(collection, canvas=self.plot)

class OnlyNumEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar(master)
        self.isNum = False
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.var.trace_add('write', self.validate)

    def validate(self, *args):
        try:
            float(self.var.get())
            self.isNum = True
        except:
            self.isNum = False


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

    RotationAngle: float = 0.
    RotationAxis: str = "x"



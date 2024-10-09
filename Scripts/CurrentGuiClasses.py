'''
Another GUI script. This time, this script creates a base class for current configurations in the GUI.
Users will basically create instances of this to customize the current.

It's basically a container for parameters to create magpylib objects
'''

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, field
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
    entries: list # contains the data extracted from each widget.
    data: dataclass
    widgets: list # reference to all the grid widgets created in functions
    isInit: bool

    # FIELD GETTERS
    def GetEntries(self):
        return self.entries
    
    #===============#
    # INITIALIZAION #
    #===============#
    def __init__(self, master, dataclass:dataclass): # initialization function
        self.isInit = False
        # keep reference to the master 
        self.master = master
        self.entries = []
        self.widgets = []

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
        self.frame.grid(row=0, column=0, sticky = "")

        # frame for table data
        self.frame1 = tk.Frame(self.frame) 
        self.frame1.grid(row=0, column=0, sticky = "")

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

        self.isInit = True
    
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
        widget = entry.widget
        info = widget.grid_info()
        rowInd = info["row"] - 1    # minus one to account for the first row being titles, var names
        colInd = info["column"]

        # Now we extract the newly edited value to allow for examination.
        entryValue = widget.get()
        
        self.GetEntries()[rowInd][self.fields[colInd]] = entryValue
        return True

    def DelEntry(self, button):
        '''
        Deletes its respective row of the entry table, as well as its data in self.entries.
        '''

        row = button.grid_info()['row'] # the row to remove

        #print(self.frame1.grid_size())
        #print(row)
        for widget in self.frame1.grid_slaves(row=row):
            widget.destroy()

        widgets = self.frame1.grid_slaves() # every widget in the frame
        
        for widget in widgets:
            widgetRow = widget.grid_info()['row']
            if widgetRow > row:
                widget.grid(row=widgetRow-1, column=widget.grid_info()['column'])
    
        self.widgets.pop(row-1)
        self.entries.pop(row-1)
        #print(self.frame1.grid_size())

    
    def NewEntry(self, *args, defaults=True):
        '''
        Creates a new row for the entry table
        
        
        if not creating a default row, you must pass an instance of a dataclass
        with the desired values.
        '''
        #print(defaults)
        if (defaults == True):
            row = self.data(self.frame1)
        else:
            #print("should run when defaults is False")
            row = args[0]
        #print("row is: ", row)
        r = self.frame1.grid_size()[1]
        dict = {} # data extracted from each row
        rowwidgets = []
        col = 0
        for i in row:
            #print(i)
            #print("the field is: ", i.paramDefault)
            # create the respective entry box
            self.widget = i.paramWidget
            dict[self.fields[col]] = self.widget.get()
            
            self.widget.grid(row = r, column = col)
            rowwidgets.append(self.widget)

            match self.widget:
                case OnlyNumEntry():
                    self.widget.bind_class("OnlyNumEntry", "<Key>", self.EntryValidateCallback)
                case ttk.Combobox():
                    self.widget.bind("<<ComboboxSelected>>", self.EntryValidateCallback)

            col += 1

        # also add delete button at the far right
        self.delButton = tk.Button(self.frame1, text="Delete")
        rowwidgets.append(self.delButton)
        self.delButton.grid(row=r, column = col)
        self.delButton.config(command=partial(self.DelEntry, self.delButton))

        # update metadata containers
        self.entries.append(dict)
        self.widgets.append(rowwidgets)
        #print(self.widgets)


    def ClearTable(self):
        '''
        deletes everything from the table. That means, everything 
        except for the first row of the frame (which has the column information)
        '''
        numRows = self.frame1.grid_size()[1]

        for row in reversed(range(1, numRows)):
            for widget in self.frame1.grid_slaves(row=row):
                widget.destroy()
        self.entries = []
        self.widgets = []

    def SetRows(self, list):
        '''
        given a list of dataclass objects, populate the table with respective rows.
        Expected to run when files are loaded. therefore, it clears the entry table.
        '''
        if (not self.isInit):
            return False

        if self.frame1.grid_size()[1] > 1:
            #print("clearing table")
            self.ClearTable()

        for row in list:
            #print("setrows for: ", row)
            self.NewEntry(row, defaults=False)
        
        return True

class CurrentEntryTable(EntryTable):
    '''
    The Entry Table for currents will have a (probably unique) graph button, so I made a subclass to extend that functionality.

    I'll probably also include the graph widget in this class for simplicity.
    '''
    collection = Collection()

    def __init__(self, master, dataclass):
        super().__init__(master, dataclass)
        #--------#
        # FIGURE #
        #--------#
        self.frame2 = tk.LabelFrame(self.master,
                                   text="Graph")
        self.frame2.grid(row=1, column=0)

        self.fig = plt.figure(figsize=(10, 10))
        self.plot = self.fig.add_subplot(1,1,1, projection="3d")
        
        self.canvas = FigureCanvasTkAgg(self.fig,
                                        master = self.frame2)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

        # draw canvas for the first time
        # is it inelegant to hard code initialization event order like this? maybe
        # toobad!
        self.GraphCoils()

    def GraphCoils(self):
        '''
        1. Extracts the data from self.entries
        2. Creates magpylib circle current objects from this data
        3. Graphs these created coils
        '''
        self.collection = Collection()
        #print(self.GetEntries())
        for row in self.GetEntries():
            pos = [float(row["PosX"]), float(row["PosY"]), float(row["PosZ"])]
            c = Circle(current=float(row["Amp"]),
                                   position=pos,
                                   diameter = float(row["Diameter"])
                                   )
            c.rotate_from_angax(float(row["RotationAngle"]), row["RotationAxis"])
            self.collection.add(c)
        
        self.plot.cla()
        show(self.collection, canvas=self.plot)
    
    def EntryValidateCallback(self, entry):
        '''
        override of base class function, graphs the configuration upon each change.
        '''
        super().EntryValidateCallback(entry)
        self.GraphCoils()
    
    def NewEntry(self, *args, defaults=True):
        super().NewEntry(*args, defaults=True)
        check = self.isInit
        if(check):
            self.GraphCoils()

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

    def Get(self, isNum=True):
        if isNum:
            return float(self.paramWidget.get())
        else:
            return self.paramWidget.get()



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

    RotationAngle: EntryTableParam = field(init=False)
    RotationAxis: EntryTableParam = field(init=False)

    def __init__(self, frame):
        self.PosX = EntryTableParam(0., master=frame)
        self.PosY = EntryTableParam(0., master=frame)
        self.PosZ = EntryTableParam(0., master=frame)

        self.Amp = EntryTableParam(1e5, master=frame)
        self.Diameter = EntryTableParam(1, master=frame)

        self.RotationAngle = EntryTableParam(0., master=frame)
        self.RotationAxis = EntryTableParam(0, ttk.Combobox, master=frame, state="readonly")
        
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
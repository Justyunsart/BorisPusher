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
import pandas as pd
import os
from GuiHelpers import CSV_to_Df
from PusherClasses import UniqueFileName
from GuiEntryHelpers import *

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
    def __init__(self, master, dataclass:dataclass, name="entry", save=True, rowInit=True): # initialization function
        self.isInit = False
        self.name = name
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
        if(rowInit):
            self.NewEntry() # add one empty row for the start

        # Button to add new rows
        self.addButton = tk.Button(self.frame,
                                   text="New Entry",
                                   command=self.NewEntry)
        self.addButton.grid(row=1, column=0, sticky="")

        if (save):
            # Save as button
            self.saveButton = tk.Button(
                self.frame,
                text="Save As",
                command=self.SaveData
            )
            self.saveButton.grid(row=1, column=1, sticky="E")
            
            # save as entry field
            self.saveEntryVal = tk.StringVar()
            self.saveEntry = tk.Entry(
                self.frame,
                textvariable=self.saveEntryVal,
                width=20
            )
            self.saveEntry.grid(row=1, column=2, sticky="E")

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
        return row

    
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

    def _SetSaveEntry(self, name:str, **kwargs):
        '''
        whenever this is called, the save entry field gets filled with the currently selected file's name.
        

        Because this base class does not include the file dropdown, it's expected that the name parameter is filled
        by its children. Otherwise, this function will just go unused.
        '''
        if(name == ""):
            self.saveEntryVal.set(self.name)
            return True
        self.saveEntryVal.set(name)
        return True
    
    def SaveData(self, dir:str, container=None, vals=None, customContainer=False):
        '''
        after reading where to save (DIR variable from somewhere),
        look at the value of the nearby entry widget and either create the file (if not present)
        or overwrite to the already existing file.

        format:
        1st line is the names of all the fields

        Every line following are values that fall under these fields.
        '''
        # this is the name of the file to save to.
        saveName = self.saveEntry.get()

        PATH = os.path.join(dir, saveName)
        #print(PATH)

        #print(container)
        #print(vals)
        # the first row is the names of all the fields.
        # get each entry in the desired format

        match customContainer:
            case True:
                match container:
                    case None:
                        KeyError("customContainer ran with True, yet no container given.")
                match vals:
                    case None:
                        KeyError("vals not provided")
                try:
                    container = self._Constructed_nested_list(dic=container, vals=vals)
                except:
                    print(f"Something went wrong when saving container. Got: {container}" )
            case False:
                try:
                    vals = [self.fields.copy()] #i want to really make sure we're working with a copy of the list
                    container = self._Constructed_nested_list(dic=self.entries, vals=vals)
                except:
                    print(f"Something went wrong when saving self.entries. Got: {self.entries}" )

        List_to_CSV(PATH, container, newline="")


    def _Constructed_nested_list(self, dic, vals):
        for entry in dic:
            vals.append(list(entry.values()))
        return vals

    
    def GetData(self):
        '''
        when called, reads the currently held data points and outputs it in a readable format.

        
        self.entries is a list of dictionaries; each list entry is a row in the table.
        Therefore, the format could be: {key = "<entry name>_<n>" : value = <dataclass instance>}
        
        
        Or a nested dictionary. I'm going with nested dictionary. It's easy, and I'm stupid.
        '''
        
        keyBase = str(self.data)

        out = {}
        lst = []
        for i in range(len(self.entries)):
            #keyName = f'{keyBase}_{i}'
            value = self.entries[i]
            lst.append(value)

        out[keyBase] = pd.DataFrame(lst)
        return out
    
    def Read_Data(self, dir=None, **kwargs):
        '''
        look at the dir of the selected input file, then turn it into rows on the entry table
        '''
        if(dir==None):
            if(self.dirWidget.fileName) == "":
                return False

            #print("reading data")
            data = CSV_to_Df(self.dirWidget.PATH.data, isNum=False, **kwargs).values.tolist() # ideally, each sublist will be a row of params for file_particle
            #print(data)

        else:
            """
            when dir != None, assume it's been provided with a valid filepath to read.
            """
            data = CSV_to_Df(dir, isNum=False).values.tolist()
        
        return data
    
    def _NewFile(self, dir:str, name:str, data=None):
        '''
        helps the programmer from having to call the many functions associated with this 
        functionality. 
        '''
        self._SetSaveEntry(name)

        if data != None:
            """
            data represents the path to copy data from. So if it is provided, the program should
            read and set that data on instantiation
            """
            self.Read_Data(dir = data)
        
        self.SaveData(dir)

    def Refresh(self):
        """
        in the event of many changes happening to the table at once,
        
        
        this method can be called at the end of those changes to sync
        widgets with self.entries.

        
        since the EntryCallback only triggers from combobox selections and 
        keypresses, this way is more efficient when there are changes caused
        by backend code.
        """
        collectedTypes = [OnlyNumEntry, ttk.Combobox]
        out = []

        size = self.frame1.grid_size()
        #indices of interest from the grid are (inclusive):
        #     - rows 1 -> end
        #     - cols 0 -> -2
        widgets = []
        for i in range(1, size[1]):
            row = self.frame1.grid_slaves(row=i) [::-1]
            widgets.append(row)

        for row in widgets:
            temp = {}
            for widget in row:
                if (type(widget) in collectedTypes):
                    info = widget.grid_info()
                    c = info["column"]
                    temp[self.fields[c]] = widget.get()
            out.append(temp)

        self.entries = out

class RotationConfigEntryTable(EntryTable):
    """
    A special kind of entry table that expects an input of data from external sources.
    """
    axisIndices = {"x" : 0,
                   "y" : 1,
                   "z" : 2}
    def __init__(self, master, data, defaults=True, *args, callable:callable=None, **kwargs):
        self.func = callable
        self.master = master
        self.data_to_fill = data
        self.defaults = defaults
        super().__init__(master=master, *args, **kwargs)

        self.onRotationEntryOpen(defaults=self.defaults, lst=self.data_to_fill)
    
    def onRotationEntryOpen(self, defaults:bool, lst:list=None):
        '''
        # parameters:
        defaults (bool) = True
            > controls whether to instantiate the table with default values.
        
        lst:list = None
            > expected when defaults = False.
            > contains the data to create the table with instead of default.
        '''
        #print(lst)
        match defaults:
            case True:
                self.NewEntry()
            
            case False:
                try:
                    self.SetRows(lst)
                except:
                    raise KeyError("'defaults' ran with False, yet no list")
    
    def OnRotationEntryClose(self):
        """
        when the entry table window is supposed to close,
        it must get its data and return it for the parent window.
        """
        for i in self.entries:
            i['RotationAngle'] = float(i['RotationAngle'])
        return self.entries
    
    def SetRows(self, list):
        """
        Before running super, format the given data from a list of dicts to a list of dataclasses.
        """
        out = []
        for data in list:
            config = RotationConfig(self.frame1,
                                    data["RotationAngle"],
                                    self.axisIndices[data["RotationAxis"]])
            out.append(config)
        #print(out)
        super().SetRows(out)

    def EntryValidateCallback(self, entry):
        super().EntryValidateCallback(entry)
        if (self.func != None):
            self.func(table=self)
    

# CURRENT ENTRY TABLE
#################################################################################################################

class CurrentEntryTable(EntryTable):
    '''
    The Entry Table for currents will have a (probably unique) graph button, so I made a subclass to extend that functionality.

    I'll probably also include the graph widget in this class for simplicity.
    '''
    collection = Collection() # magpy object for visualization
    rotations = [] # container to store coil rotation info.

    """
    Class settings, defaults
    """
    defaultFileName = "Coil"
    axisIndices = {"x" : 0,
                   "y" : 1,
                   "z" : 2}

    def __init__(self, master, dataclass, dirWidget, graphFrame, defaults):
        self.dirWidget = dirWidget
        self.DIR_coilDefs = defaults
        super().__init__(master, dataclass)
        self.saveButton.configure(command=partial(self.SaveData, self.dirWidget.dir))

        # JAWK TAWAH attach to the thanggg 
        self.dirWidget.PATH.attach(self)

        #--------#
        # FIGURE #
        #--------#
        self.frame2 = graphFrame
        self.frame2.grid(row=0, column=1)

        self.fig = plt.figure(figsize=(5, 5))
        self.plot = self.fig.add_subplot(1,1,1, projection="3d")
        
        self.canvas = FigureCanvasTkAgg(self.fig,
                                        master = self.frame2)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

        self.saveButton.config(command = partial(self.SaveData, self.dirWidget.dir))

        self.addButton.config(command=self._new_Button_Callback)
        
        # draw canvas for the first time
        # is it inelegant to hard code initialization event order like this? maybe
        # toobad!
        self.Read_Data()
        self._SetSaveEntry(self.dirWidget.fileName.get())
        #self.GraphCoils()

    def GraphCoils(self):
        '''
        1. Extracts the data from self.entries
        2. Creates magpylib circle current objects from this data
        3. Graphs these created coils
        '''
        #print(self.rotations)
        #print("graph reset")
        self.collection = Collection()
        #print(self.GetEntries())
        for i in range(len(self.GetEntries())):
            row = self.GetEntries()[i]
            pos = [float(row["PosX"]), float(row["PosY"]), float(row["PosZ"])]
            c = Circle(current=float(eval(row["Amp"])),
                                   position=pos,
                                   diameter = float(row["Diameter"])
                                   )
            for rotation in self.rotations[i]:
                #print(rotation)
                c.rotate_from_angax(float(rotation["RotationAngle"]), rotation["RotationAxis"])
            self.collection.add(c)
        
        self.plot.cla()
        show(self.collection, canvas=self.plot, canvas_update = True, backend="matplotlib")
        self.canvas.draw()
        return True

    def EntryValidateCallback(self, entry):
        '''
        override of base class function, graphs the configuration upon each change.
        '''
        super().EntryValidateCallback(entry)
        self.GraphCoils()
    
    def NewEntry(self, *args, defaults=True):
        super().NewEntry(*args, defaults=defaults)
        
        self.entries[-1]["Rotations"].config(command=partial(self.NewWindow, self.entries[-1]["Rotations"]))
        if(self.isInit):
            self.rotations.append([{"RotationAngle": 0, "RotationAxis": 'x'}]) # this line does not scale with changing default values of the class.

    def _new_Button_Callback(self):
        """
        to control the call of self.GraphCoils(), call it only after pressing a new entry button.
        So that when newentry is called from other functions, it doesn't try to run graphcoils on accident.
        """
        self.NewEntry()
        self.GraphCoils()

    def Read_Data(self, dir=None):
        data = super().Read_Data(dir=dir, converters={"RotationAngle":tryEval, "RotationAxis":tryEval})
        coils = []
        rotations = []
        #print(data)

        # TODO: mess with this function to incorporate the new method for rotation.
        for row in data:
            coil = CircleCurrentConfig(self.frame1, 
                                     px = row[0], 
                                     py = row[1], 
                                     pz = row[2], 
                                     amp= row[3],
                                     dia= row[4]
                                     #angle = row[5],
                                     #axis=self.axisIndices[row[6]]
                                     )
            #print(particle.py.paramDefault)
            coils.append(coil)
            
            #print(type(row[5]))
            match row[5]:
                case float():
                    rotations.append([{"RotationAngle":(row[5]), "RotationAxis":(row[6])}])
                case int():
                    rotations.append([{"RotationAngle":(row[5]), "RotationAxis":(row[6])}])
                case list():
                    out = []
                    for i in range(len(row[5])):
                        out.append({"RotationAngle":(row[5])[i], "RotationAxis":(row[6])[i]})
                    rotations.append(out)
        
        #print(coils)
        self.rotations = rotations
        #print(rotations)
        self.SetRows(coils)
        #print(self.entries)
        return True

    def SetRows(self, list):
        super().SetRows(list)
        self.GraphCoils()
    
    def GetData(self):
        value = self.collection
        out = dict(coils = value)
        out["Coil File"] = self.saveEntryVal.get()
        return out
    
    def SaveData(self, dir:str, container=None, customContainer=False):
        # make a copy of self.entries just for this
        container = self.entries.copy()
        customContainer=True #flag this class as needing a custom container
        #print(self.rotations)
        # combine the entries and rotations container
        for i in range(len(self.entries)):
            container[i]["RotationAngle"] = str([j["RotationAngle"] for j in self.rotations[i]])
            container[i]["RotationAxis"] = str([j["RotationAxis"] for j in self.rotations[i]])
            # remove the 'Rotations' key; leftover from the dataclass that needs to be cut
            del container[i]['Rotations']
        
        vals = [list(container[0].keys())]
        super().SaveData(dir, container, vals, customContainer)

        # In addition to the super, also update the selected file's value in the field dropdown
        if self.saveEntryVal.get() not in self.dirWidget["values"]:
            self.dirWidget["values"] += (self.saveEntryVal.get(),)
            self.dirWidget.current(len(self.dirWidget["values"]) - 1)
    
    def update(self, subject):
        '''
        rerun read data to reset the table upon the selected input file being changed.
        '''
        self.Read_Data()
        self._SetSaveEntry(self.dirWidget.fileName.get())

    def Create_Mirror(self, fileName:str, templateName:str):
        '''
        1. create a new file to work with
        2. in the new file, set up (with default params) a mirror configuration
            > 2 coils symmetric about the origin, displaced in the x-axis
            > They also have the same charge
        '''
        # 1. Get the name of the file this function will create.
        name = UniqueFileName(DIR=self.dirWidget.dir, fileName=fileName)
        DIR_mirror = os.path.join(self.DIR_coilDefs, templateName)

        #print("name is: ", name)
        #print("I should be made in: ", os.path.join(self.dirWidget.dir, name))
        
        # 2. Create and populate the file.
        self._NewFile(dir=self.dirWidget.dir, name=name, data=DIR_mirror)
    
    def Refresh(self):
        super().Refresh()
        self.GraphCoils()

    def DelEntry(self, button):
        row = super().DelEntry(button)
        self.rotations.pop(row)

    
    def NewWindow(self, wid):
        '''
        passed to the entry row: opens a new window containing the rotation entry table.
        '''
        #print(self.rotations)
        row = wid.grid_info()["row"] # so we know which particle this window is for
        #print(row)

        # get info to best place this window on the screen.
        x_pos = wid.winfo_rootx()
        y_pos = wid.winfo_rooty()

        # Create the New Window
        newWin = tk.Toplevel(self.master)
        newWin.title(f"Configure Rotation(s) for particle {row}")

        # Spawn the Entry Table element
        frame = tk.LabelFrame(newWin, text="Rotations Table")
        frame.grid(row=0, column=0)
        table = RotationConfigEntryTable(defaults=False, data=self.rotations[row-1], master=frame, dataclass=RotationConfig, save=False, rowInit=False,
                                         callable=partial(self._graph_callback, row, table=None))

        # Get the size of the window with these elements added in.
        newWin.update()
        winX = newWin.winfo_width()
        winY = newWin.winfo_height()

        # Set the geometry
        newWin.geometry(f'+{x_pos-winX}+{y_pos-(winY//2)}')

        # Set up the data collection function onclose.
        newWin.protocol('WM_DELETE_WINDOW', partial(self._entry_window_close, table, newWin, row))
    
    def _entry_window_close(self, table:RotationConfigEntryTable, window:tk.Toplevel, row:int):
        self.rotations[row-1] = table.OnRotationEntryClose()
        #print(self.rotations)

        window.destroy()
    def _graph_callback(self, row, table:RotationConfigEntryTable):
        self.rotations[row-1] = table.OnRotationEntryClose()

        self.GraphCoils()

'''
Another GUI script. This time, this script creates a base class for current configurations in the GUI.
Users will basically create instances of this to customize the current.

It's basically a container for parameters to create magpylib objects
'''
import tkinter.ttk
from collections import defaultdict

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

from functools import partial

from magpylib import show
from magpylib import Collection
from magpylib.current import Circle
from files.PusherClasses import UniqueFileName
from Gui_tkinter.funcs.GuiEntryHelpers import *
from ast import literal_eval

from settings.configs.funcs.config_reader import runtime_configs
from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import manager_1, m1f1
from settings.defaults.coils import default_coil, coil_cust_attr_name
from definitions import PLATFORM, NAME_COILS

from system.temp_file_names import param_keys

if PLATFORM != "win32":
    from xattr import setxattr
else:
    import os

from pathlib import Path

class EntryTable():
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

    # FIELD GETTERS
    def GetEntries(self, csv=False):
        """
        Moving away from keeping and updating data with self.entries. Instead, I want to retain dataclass instances (since I'm creating these classes anyway).
        This function will get the attribute self.instances (a list of currently active dataclass instances) and return all their data as a dictionary.

        This will only run when we want to zip file contents or something.
        """
        out = []
        for entry in self._instances:
            out.append(entry.get_dict(csv))

        if(not csv): # csv == False
            """
            When the function is called with csv == False, the caller is requesting a view of the data that works for graphing.
                The dict should be organized like: [{dict1}, {dict2}], in which:
                    Each dict holds both the row and rotation data
                    Each dict also represents a new row.

            This is accomplished with the above code by running the dataclass's get_dict() callable with csv == False.
            """
            return out

        else: # csv == True
            """
            When function is called with csv == True, the caller is requesting a view of the data that directly works for converting to a pd.DataFrame object.
                The dict should be organized like: {'key':[value1, value2,], ...}, in which:
                    Key - each column variable
                    Value - a list containing the respective entry for each row.

            This can be accomplished by merging the list of dictionaries created before the if-else block. Because it ran get_dict() with csv == True,
            each dict is formatted with the rotation attributes without nesting.
            """
            # a dictionary that fills missing values with an empty list.
            out_merged = defaultdict(list)

            # iterate over the out list of dictionaries, extending the empty list with stored values.
            for d in out:
                for key, value in d.items():
                    # value is expected to be a list
                    out_merged[key].extend(value)

            return out_merged
    
    def _updateTempFile(self, field, val):
        def set_nested_value(d, keys, value):
            """Set a value in a nested dictionary given a list of keys."""
            for key in keys[:-1]:
                d = d.setdefault(key, {})  # ensures intermediate dicts exist
            d[keys[-1]] = value

        # read the dictionary
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])

        # if the function is given a list instead of a string to look up, call the nested function
        # to edit the nested dictionary.
        if isinstance(field, list):
            set_nested_value(d, field, val)
        else:
            d[field] = val
        #print(f"RUNNING FROM _updateTempFile from CurrentGuiClasses.py, line 94")
        #print(d)
        write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)
    #===============#
    # INITIALIZAION #
    #===============#
    def __init__(self, master, dataclass:dataclass, name="entry", save=True, rowInit=True, doDirWidget=True): # initialization function
        self.isInit = False # initialization is false at the beginning.
        # keep reference to the master 
        self.master = master
        self.entries = []
        self.widgets = []
        self._instances = []

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

        # CHILDREN FRAME IN PARENT.
        # optional header frame
        self.frame0 = tk.Frame(self.frame)
        self.frame0.grid(row=0, column=0, sticky="")
        
        # frame for table data
        self.frame1 = tk.Frame(self.frame) 
        self.frame1.grid(row=1, column=0, sticky = "")

        # frame for features at the bottom of the table.
        self.frame2 = tk.Frame(self.frame)
        self.frame2.grid(row=2, column=0, sticky="")

        # create top row of the data table (name of vars)
        for i in range(self.numcols): 
            self.titleLabel = tk.Label(self.frame1,
                                       text=str(self.fields[i]))
            self.titleLabel.grid(row=0, column=i)
        if(rowInit):
            self.NewEntry() # add one empty row for the start

        # Button to add new rows
        self.addButton = tk.Button(self.frame2,
                                   text="New Entry",
                                   command=self.NewEntry)
        self.addButton.grid(row=0, column=0, sticky="")

        if (save):
            saveFrame = tk.Frame(self.frame2)
            saveFrame.grid(row=0, column=1)
            # Save as button
            self.saveButton = tk.Button(
                saveFrame,
                text="Save As",
                command=self.SaveData
            )
            self.saveButton.grid(row=0, column=1, sticky="W")
            
            # save as entry field
            self.saveEntryVal = tk.StringVar()
            self.saveEntry = tk.Entry(
                saveFrame,
                textvariable=self.saveEntryVal,
                width=20
            )
            self.saveEntry.grid(row=0, column=0, sticky="W")

        self.isInit = True
    
    #===========#
    # CALLBACKS #
    #===========#
    
    def EntryValidateCallback(self, entry, check_float=True):
        '''
        Callback function that is called by entryboxes.

        When a user updates an entry box, call this function to:
            1. Validate entry type (not implemented here atm)
            2. Update its corresponding field in self.entries
        '''
        #print(f"EntryTable.EntryValidateCallback called, self.entries is {self.entries}")
        # To get the corresponding index and field in self.entries, we need to first extract the grid position of the entry box.

        # Row index = self.entry index
        # Column index = field index
        widget = entry.widget
        info = widget.grid_info()
        rowInd = info["row"] - 1    # minus one to account for the first row being titles, var names
        colInd = info["column"]
        #print(colInd)

        #print(self.master)
        # Now we extract the newly edited value to allow for examination.
        entryValue = widget.get()
        #print(entryValue)
        # Don't update anything if the entryValue is illegal.
        #   If it's blank or cannot be converted into a float.
        if check_float:
            try:
                float(entryValue)
                widget.untrigger_warning()  # remove the widget's warned state if it is warned.
            except:
                # if the value is illegal, then trigger the widget's warning state.
                widget.trigger_warning()
                return False
        instance = self._instances[rowInd] # the dataclass instance of the correspondng row
        instance.iterables[colInd].paramWidget.var.set(entryValue) # modify the dataclass's corresponding value according the the colInd.
        #self.GetEntries()[rowInd][self.fields[colInd]] = entryValue

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
        #self.entries.pop(row-1)
        self._instances.pop(row-1)
        #print(self.frame1.grid_size())
        return row

    
    def NewEntry(self, *args, defaults=True):
        '''
        Creates a new row for the entry table
        
        
        if not creating a default row, you must pass an instance of a dataclass
        with the desired values.

        if called at the time of more than one row in the table, then just copies the row at the last index
        '''
        """
        #print(self.instances)
        if (defaults == True):
            row = self.data(self.frame1)
            #print(row)
            self._instances.append(row)
            #print(self.instances)
        """
        if len(self._instances) >= 1 and defaults == True:
            # when defaults are not provided, and there is more than 1 row.
            #print("HEY!!!!!!!!")
            #row = self._instances[-1]
            #print(self._instances[-1])
            #row = self.data(self._instances[-1])
            row = self.data(self.frame1)
            self._instances.append(row)
        
        elif len(self._instances) == 0 and defaults == True:
            row = self.data(self.frame1)
            #print(row)
            self._instances.append(row)

        else:
            # when defaults is not provided, this function is being fed
            # pre-populated values.
            row = args[0]
            self._instances.append(row)
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
                    self.widget.bind("<KeyRelease>", self.EntryValidateCallback)
                case ttk.Combobox():
                    self.widget.bind("<<ComboboxSelected>>", self.EntryValidateCallback)

            col += 1

        # also add delete button at the far right
        self.delButton = tk.Button(self.frame1, text="Delete")
        rowwidgets.append(self.delButton)
        self.delButton.grid(row=r, column = col)
        self.delButton.config(command=partial(self.DelEntry, self.delButton))

        # update metadata containers
        #self.entries.append(dict)
        self.widgets.append(rowwidgets)
        #print(self.widgets)
        #self.instances.append(row)
        return True


    def ClearTable(self):
        '''
        deletes everything from the table. That means, everything 
        except for the first row of the frame (which has the column information)
        '''
        numRows = self.frame1.grid_size()[1]

        for row in reversed(range(1, numRows)):
            for widget in self.frame1.grid_slaves(row=row):
                widget.destroy()
                #print(f"row destroyed")
        self.entries.clear()
        self.widgets.clear()
        #print(f"before clear: {self.instances}")
        self._instances.clear()
        #print(f"after clear: {self.instances}")

    def SetRows(self, list):
        '''
        given a list of dataclass objects, populate the table with respective rows.
        Expected to run when files are loaded. therefore, it clears the entry table.
        '''
        #print(self.instances)

        if self.frame1.grid_size()[1] > 1:
            #print("clearing table")
            self.ClearTable()
        #print(self.instances)
        if list is not None:
            """
            A list being provided = read rows to be initialized and added to instances.
            """
            for row in list:
                #print(row)
                self.NewEntry(row, defaults=False)
                #print(self.instances)
        else:
            print(f"SetRows called with NONE for parameter 'list'")
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
                    #container = self._Constructed_nested_list(dic=self.entries, vals=vals)
                    container = self._Constructed_nested_list(dic=self.GetEntries(), vals=vals)
                except:
                    print(f"Something went wrong when saving self.entries. Got: {self.entries}" )

        #print(PATH)
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
        """
        for i in range(len(self.entries)):
            #keyName = f'{keyBase}_{i}'
            value = self.entries[i]
            lst.append(value)
        """

        out[keyBase] = pd.DataFrame(self.GetEntries())
        return out
    
    def Read_Data(self, dir=None, eval_ind=None, dct=False, **kwargs):
        '''
        look at the dir of the selected input file, then turn it into rows on the entry table
        (param: ) dir: a string path to the input file to read. It defaults to None, so that just calling the function will read the currently selected value from the corresponding dropdown instead. 
        '''
        # first, clear the table if needed.
        if self.frame1.grid_size()[1] > 1:
            #print("clearing table")
            self.ClearTable()

        # if eval_ind is not None, then assume it is provided with a tuple of indices to run ast_eval on.
        # the way this will work is that the program will create a converter dict. in which the keys are the indices and the values are literal eval.
        converter = {}
        if eval_ind is not None:
            for ind in eval_ind:
                converter[int(ind)] = literal_eval
        try:
            if(dir==None):
                # READ TO THE SELECTED DIRECTORY IF NO EXPLICIT DIR PROVIDED
                if((self.dirWidget.fileName) == "") or (self.dirWidget.fileName is None):
                    return False
                #print(self.dirWidget.PATH.data)
                data = CSV_to_Df(self.dirWidget.PATH.data, isNum=False, converters=converter, **kwargs)

            else:
                # WHEN A DIR IS PROVIDED ON FUNCTION CALL
                # READ SPECIFIED DIR IF CALLED w/ IT
                data = CSV_to_Df(dir, isNum=False, converters=converter)
        
        except ValueError:
            """
            This block will run if there is an issue with reading from the selected file.
            (the most common case being that the csv formatting has changed.)

            In this case, the program will convert read columns into lists, assuming it read
            a single value that's not in a data structure.
            """
            data = CSV_to_Df(self.dirWidget.PATH.data, False)
            for i in eval_ind:
                data.iloc[:,i] = data.iloc[:,i].apply(lambda x: [x])
        #print(data)
        if dct:
            data = data.to_dict(orient='records')
        else:
            data = data.values.tolist()
        #print(data)
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


        #self.entries = out

######################################
# ENTRY TABLE TOPLEVEL FOR ROTATIONS #
#####################################################################################
class RotationConfigEntryTable(EntryTable):
    """
    A special kind of entry table that expects an input of data from external sources.
    It is opened when a button is pressed in a current entry table.
    """
    axisIndices = {"x" : 0,
                   "y" : 1,
                   "z" : 2}
    columnTitles = ['Rotation Angle', 'Rotation Axis']
    isActive = False
    def __init__(self, master, angle_data, ax_data, defaults=True, *args, callable:callable=None, parent, **kwargs):
        self.data = RotationConfig
        
        self.func = callable
        self.master = master
        self.data_to_fill = np.array([angle_data, ax_data]).T
        self.defaults = defaults
        self.parent = parent
        super().__init__(master=master, doDirWidget=False, *args, **kwargs)

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
                self.NewEntry(defaults=True)
            
            case False:
                try:
                    self.SetRows(lst)
                except:
                    raise KeyError("'defaults' ran with False, yet no list")
        self.isActive = True
        #print(self.isActive)
    
    def OnRotationEntryClose(self):
        self.isActive = False
        return self.ReturnRotations()
    
    def ReturnRotations(self):
        """
        when the entry table window is supposed to close,
        it must get its data and return it for the parent window.
        """
        out = self.GetEntries()
        #print(out)
        return out
    
    def SetRows(self, list):
        """
        Before running super, format the given data from a list of dicts to a list of dataclasses.
        """
        lst = []
        for data in self.data_to_fill:
            config = RotationConfig(self.frame1,
                                    data[0],
                                    self.axisIndices[data[1]])
            lst.append(config)
        #print(self.instances)
        super().SetRows(lst)

    def EntryValidateCallback(self, entry):
        #print(self.isActive)
        if not isinstance(entry.widget, tkinter.ttk.Combobox):
            if (self.isActive):
                super().EntryValidateCallback(entry, check_float=True)
            else:
                self.parent.EntryValidateCallback(entry, check_float=True)
        if (self.func != None):
            self.func(table=self)

    def DelEntry(self, button):
        super().DelEntry(button)
        self.EntryValidateCallback
        if (self.func != None):
            self.func(table=self)
    

# CURRENT ENTRY TABLE
#################################################################################################################

class CurrentEntryTable(EntryTable):
    '''
    The Entry Table for currents will have a (probably unique) graph button, so I made a subclass to extend that functionality.
    I'll probably also include the graph widget in this class for simplicity.

    (param: ) master: the parent frame that holds this widget.
    (param: ) dataclass: a container class with the varaible names and widgets to produce (located in GuiEntryHelpers.py)
    (param: ) graphFrame: a tk.Frame or subclass that the graphical representation of the current config will be.
    (param: ) defaults: a path pointing to the DIR containing default options (hexahedron/mirror config)
        You can think of 'defaults' like 'presets'.
    (param: ) DIR: the path to the dir containing all the saved config files of the desired dataclass.
    '''

    def __init__(self, master, dataclass, graphFrame, DIR, graph_toolbar = False, collection_key=None, path_key=None, name_key=None):
        self.collection = Collection() # magpy object for visualization
        self.rotations = [] # container to store coil rotation info.
        # self.lim: the max. offset of the coil in the entry table.
        self.lim:Data = Data() # when updated, outside subscribers will run their respective update functions.
        self.collection_key = collection_key
        self.path_key = path_key
        self.name_key = name_key

        #self.instances = [] # references to the instantiated dataclasses (rows).
        self.defaultFileName = "Coil"
        self.DIR = DIR

        super().__init__(master, dataclass)
        self.dirWidget = FileDropdown(master=self.frame0, dir=self.DIR, default=self._Create_Default_File)
        self.dirWidget.grid(row=0, column=0)
        self.saveButton.configure(command=partial(self.SaveData, self.dirWidget.dir))

        # dirWidget's PATH var is an observer class, which this table will watch and update
        # when called.
        self.dirWidget.PATH.attach(self)

        #--------#
        # FIGURE #
        #--------#
        # create graph properties
        self.frame2 = graphFrame
        #self.frame2.grid(row=1, column=0)

        self.fig = plt.figure(figsize=(2.5, 2.5))
        self.plot = self.fig.add_subplot(1,1,1, projection="3d")
        
        self.canvas = FigureCanvasTkAgg(self.fig,
                                        master = self.frame2)
        if(graph_toolbar):
            toolbar = NavigationToolbar2Tk(self.canvas, pack_toolbar=False)
            
            # make sure they are instantiated
            toolbar.update()
            self.canvas.draw()

            # pack graph stuff
            toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # configure buttons w/ appropriate callbacks
        self.saveButton.config(command = partial(self.SaveData, self.dirWidget.dir))
        self.addButton.config(command=self._new_Button_Callback)
        
        # draw canvas for the first time
        self.update()

    def read_last_used(self):
        d = TEMPMANAGER_MANAGER.files[m1f1]
        try:
            self.dirWidget.combo_box.set(d[self.name_key])
        except:
            pass


    def _Create_Default_File(self, path):
        """
        run whenever the DIR for input files is empty.
        creates a file with the dataclass's default values.
        """
        '''
        #print(f"new file creation attempt")
        default_dataclass = self.data(self.frame1) # construct dataclass with default parameters
        
        
        df = default_dataclass.get_dict(to_csv=True) # we need to format this dict. so that rotations and angles are lists.
        #print(df)
        df = pd.DataFrame.from_dict(df)
        #print(df)


        def_name = "Default_Dan"
        self._SetSaveEntry(def_name)
        df.to_csv(os.path.join(self.DIR.path.data, def_name), index=False)
        '''
        self.Create_From_Preset(default_coil, graph=False, path=path)


    def GraphCoils(self):
        '''
        1. Extracts the data from self.entries
        2. Creates magpylib circle current objects from this data
        3. Graphs these created coils
        '''

        #print(self.instances)
        self.collection = Collection()
        for i in range(len(self.GetEntries())):
            row = self.GetEntries()[i]
            #print(row)
            pos = [float(row["PosX"]), float(row["PosY"]), float(row["PosZ"])]
            c = Circle(current=float(eval(row[self.data.power_name])),
                                   position=pos,
                                   diameter = float(row["Diameter"])
                                   )
            for j in range(len(row['Rotations']['Angles'])):
                dict = row['Rotations']
                c.rotate_from_angax(float(dict['Angles'][j]), dict['Axes'][j])
            self.collection.add(c)
        
        self.plot.cla()
        show(self.collection, canvas=self.plot, canvas_update = False, backend="matplotlib")
        self.plot.get_legend().remove()
        self.fig.tight_layout()
        self.canvas.draw()

            # Update tempfile entry for the coil collection object.
        self._updateTempFile(self.collection_key, self.collection)
        self._updateTempFile(self.path_key, self.dirWidget.PATH.data)
        self._updateTempFile(self.name_key, str(Path(self.dirWidget.PATH.data).name))
        #print(f"Collection updated: {self.collection_key}")
        return True

    def EntryValidateCallback(self, entry, check_float=True):
        '''
        override of base class function, graphs the configuration upon each change.
        '''
        #print(self.data)
        #print(f"CurrentGuiClasses.CurrentEntryTable.EntryValidateCallback: self.entries is: {self.entries}")
        self.GraphCoils() if super().EntryValidateCallback(entry) else None
        
        return True
    
    # Will not be used anymore, once the class moves to storing values via dataclass instances instead of a dict.
    def NewEntry(self, *args, defaults=True):
        #print("new entry run")
        #print(self.instances)
        # run the NewEntry function and append the returned row to the instances list.
        super().NewEntry(*args, defaults=defaults)
        widget = self._instances[-1].Rotations.paramWidget

        self._instances[-1].Rotations.paramWidget.config(command=partial(self.NewWindow, widget))
        #if(self.isInit):
        #    self.rotations.append([{"RotationAngle": 0, "RotationAxis": 'x'}]) # this line does not scale with changing default values of the class.

    def DelEntry(self, button):
        super().DelEntry(button)
        self.GraphCoils()

    def _new_Button_Callback(self):
        """
        to control the call of self.GraphCoils(), call it only after pressing a new entry button.
        So that when newentry is called from other functions, it doesn't try to run graphcoils on accident.
        """
        self.NewEntry()
        self.GraphCoils()

    def Finalize_Reading(self, coils, graph=True):
        """
        The final steps of reading information.
        Sets the rows of the table to the provided values and updates the graph.
        """
        # The dataclass instances will be added to self.instances after getting processed by self.SetRows().
        #print(self.instances)
        self.SetRows(coils)

        # used for graphing alongside an axis.
        coord = abs(np.array([coils[0].PosX.get(),coils[0].PosY.get(),coils[0].PosZ.get()], dtype=float))
        self.axis = GetAxis(coord)
        self.setLim(coord[self.axis])

        # after everything is done, you can graph coils.
        if graph:
            self.GraphCoils()
        return True
        

    def Read_Data(self, dir=None):
        """
        Expands the Read_Data method of its parent because of the (specialized) requirement
        of some parameters not fitting in a csv format.
        """
        #print(self.dirWidget.dir.path.data)

        data = super().Read_Data(dir=dir, eval_ind=self.data.eval_inds, dct=True)

        # REMINDER: these dataclass specific info. should be contained within the class instances instead.
        coils = []
        
        for row in data:
            # unpack each row as a coil arg.
            # each dataclass is constructed like: master, *args
            coil = self.data(self.frame1, **row)
            coils.append(coil)

        self.Finalize_Reading(coils)

            # update tempfile for the coil file path
        self._updateTempFile(self.path_key, self.dirWidget.PATH.data)
        self._updateTempFile(self.name_key, str(Path(self.dirWidget.PATH.data).name))
        return True
    
    def GetData(self):
        value = self.collection
        out = dict(coils = value)
        out["Coil File"] = self.saveEntryVal.get()
        return out
    
    def SaveData(self, dir:str, container=None, customContainer=False, isFirst=False):
        # make a copy of self.entries just for this
        #container = self.entries.copy()
        if(container == None):
            container = self.GetEntries(csv=True)
        
        filename = self.saveEntryVal.get()
        df = pd.DataFrame.from_dict(container)
        df.to_csv(os.path.join(self.DIR.path.data, filename), index=False)

        if not isFirst: #isFirst = initial reading before everything is initialized.
            # In addition to the super, also update the selected file's value in the field dropdown
            if self.saveEntryVal.get() not in self.dirWidget.combo_box['values']:
                self.dirWidget.combo_box["values"] += (self.saveEntryVal.get(),)
                self.dirWidget.combo_box.current(len(self.dirWidget.combo_box["values"]) - 1)
    
    def update(self, subject=None):
        '''
        rerun read data to reset the table upon the selected input file being changed.
        '''
        #print(f"currentEntryTable.update: table updated")
        self.Read_Data()
        self._SetSaveEntry(self.dirWidget.fileName.get())

    
    def Create_From_Preset(self, preset, graph=True, path=None):
        """
        Say that there are predefined configurations that need to be loaded at
        the press of a button (eg. mirror, hexahedron shapes).
        These presets' information is stored internally as classes that return a list of
        container classes.

        This function parses this output, then does everything needed for file creation and reading.
        
        It's important that the container classes in the preset callable has the same order of params
        as the dataclass used in the table!!

        To see an example of how presets are written, look at settings.defaults.coils.py.
        """
        # explicitly clear the table. Will be called later in self.SetRows(), but still.
        self.ClearTable()

        # parse the preset callable output
        info = preset.config # list of dataclass values
        parsed = []
        for row in info:
            # MAKE SURE THE PRESETS HAVE THE SAME ORDER OF INSTANCE ATTRIBUTES AS THE DATACLASS CONSTRUCTOR!!
            row_values = row.__dict__
            #print(row_values)
            # the row_values list is passed as positional arguments.
            parsed.append(self.data(self.frame1, **row_values))
        #print(parsed)
        self.Finalize_Reading(parsed, graph=graph)

        isFirst = True
        if path is None:
            path = self.dirWidget.dir.path.data
            isFirst = False

        # get a unique filename (numbered if duplicates exist)
        name = UniqueFileName(DIR=path, fileName=preset.name)
        self._SetSaveEntry(name)

        self.SaveData(dir=path, isFirst=isFirst)

            # add metadata to keep track of the preset used
        if PLATFORM != 'win32':
            setxattr(os.path.join(path, name), coil_cust_attr_name, preset._attr_val)
        else:
            with open(f"{os.path.join(path, name)}:{coil_cust_attr_name}", "w") as ads:
                ads.write(str(preset._attr_val))
            #os.setxattr(os.path.join(path, name), coil_cust_attr_name, preset._attr_val)

        #print(self.GetEntries())
        return True

    """
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
    """
    
    def Refresh(self):
        super().Refresh()
        self.GraphCoils()

    def GraphB(self, fig, root, cax):
        """
        with a mpl subplot as an input, graph the currently selected magnetic coil's B field's cross section.
        """
        c = self.collection
        l = self.getLim() + 1

        
        # construct grid for the cross section
        x = np.linspace(-l, l, 100)
        z = np.linspace(-l, l, 100)
        y = np.array([0])

        grid = np.array(np.meshgrid(x,y,z)).T #shape = (100, 100, 3, 1)
        grid = np.moveaxis(grid, 2, 0)[0] #shape = (100, 100, 3)
        
        X, _, Y = np.moveaxis(grid, 2, 0) #3 arrays of shape (100, 100)

        # calculate B field for the entire grid
        Bs = np.array(c.getB(grid)) # [bx, by, bz]
        Bx, _, By = np.moveaxis(Bs, 2, 0)
        
        '''
        Bs shape: (step, step, 3)
        '''
        # gather arguments for the streamplot

        stream = fig.streamplot(X, Y, Bx, By, color=np.log(np.linalg.norm(Bs, axis=2)), density=1)
        #stream = fig.streamplot(X, Z, U, V, color= Bamp, density=2, norm=colors.LogNorm(vmin = Bamp.min(), vmax = Bamp.max()))
        fig.set_xlabel("X-axis (m)")
        fig.set_ylabel("Z-axis (m)")
        fig.set_title("Magnetic Field Cross Section on the X-Z plane at Y=0", pad=20)
    
        cbar = root.colorbar(stream.lines, cax=cax)
        cbar.ax.set_title('log. of B-norm')
    
    def NewWindow(self, wid, *args):
        '''
        passed to the entry row: opens a new window containing the rotation entry table.
        '''
        #print(self.rotations)
        row = wid.grid_info()["row"] # so we know which particle this window is for
        angles = self._instances[row-1].rotation_angles
        axes = self._instances[row-1].rotation_axes

        # get info to best place this window on the screen.
        x_pos = wid.winfo_rootx()
        y_pos = wid.winfo_rooty()

        # Create the New Window
        newWin = tk.Toplevel(self.master)
        newWin.title(f"Configure Rotation(s) for Coil {row}")

        # Spawn the Entry Table element
        frame = tk.LabelFrame(newWin, text="Rotations Table")
        frame.grid(row=0, column=0)

        # identify whether the angle data is empty or not
        defaults = True if len(angles) == 0 else False
        #print(args[0])

        table = RotationConfigEntryTable(defaults=defaults, angle_data = angles, ax_data = axes, master=frame, dataclass=RotationConfig, save=False, rowInit=False,
                                         callable=partial(self._graph_callback, row, table=None), parent = self)

        # Get the size of the window with these elements added in.
        newWin.update()
        winX = newWin.winfo_width()
        winY = newWin.winfo_height()

        # Set the geometry
        newWin.geometry(f'+{x_pos-winX}+{y_pos-(winY//2)}')

        # Set up the data collection function onclose.
        newWin.protocol('WM_DELETE_WINDOW', partial(self._entry_window_close, table, newWin, row))

        newWin.bind('<FocusOut>', partial(self._force_close_window, newWin))
        newWin.bind('<<Save_Close>>', lambda e: self._entry_window_close(table, newWin, row))
        newWin.focus_set()

    """
    Closes the toplevel window if the focus has shifted outside the window.
    """
    def _force_close_window(self, newWin, event):
        # made into an internal func so that we can delay it (ensure the focus is set properly when run)
        def check_focus():
            try:
                focused_widget = event.widget.focus_get()

                if focused_widget is None or not str(focused_widget).startswith(str(event.widget)):
                    #print(f"should be destroying window")
                    newWin.event_generate('<<Save_Close>>')
                else:
                    pass
            except KeyError:
                # KeyError will happen in combobox widgets, as they create a popdown widget on click.
                # We ignore these because we know that a combobox widget will still maintain focus on toplevel.
                pass
        event.widget.after(10, check_focus)

    def _entry_window_close(self, table:RotationConfigEntryTable, window:tk.Toplevel, row:int):
        #print(f"entry window close protocol run.")
        dict_lst = table.OnRotationEntryClose()
        #print(dict_lst)
        self._instances[row-1].rotation_angles = [r["RotationAngle"] for r in dict_lst]
        self._instances[row-1].rotation_axes = [r["RotationAxis"] for r in dict_lst]
        #print(self.instances[row-1].rotation_angles)

        window.destroy()
    def _graph_callback(self, row, table:RotationConfigEntryTable):
        dict_lst = table.ReturnRotations()
        self._instances[row-1].rotation_angles = [r["RotationAngle"] for r in dict_lst]
        self._instances[row-1].rotation_axes = [r["RotationAxis"] for r in dict_lst]
        
        try:
            self.GraphCoils()
        except ValueError:
            """
            This block will trigger when graphing is impeded for whatever reason.
                eg. when a user has erased an entry of its contents.
            Ignores the error to avoid pinging the terminal.
            """
            pass
        

    def setLim(self, val):
        """
        when called, sets the internal lim property.
        """
        self.lim.data = val
        self.lim.notify()

    def getLim(self) -> float:
        """
        for external graphing functions that require this value, so they know how to set the 2d
        x-axis.
        """
        return self.lim.data
    
    def init_temp(self, lu):
        if lu is not None and lu[self.name_key] in os.listdir(os.path.join(runtime_configs["Paths"]['Inputs'], NAME_COILS)):
            try:
                self.dirWidget.combo_box.set(lu[self.name_key])
            except KeyError:
                pass

if __name__ == "__main__":
    from pathlib import Path
    import os
    """
    Create a tk object w/ entry tables to test thingies.
    """
    # application root
    root = tk.Tk()

    # main window
    root_frame = tk.Frame(root)
    graph_frame = tk.Frame(root)

    # get DIRs
    path_root = str(Path(__file__).resolve().parents[1]) #Expected: '/BorisPusher/...'
    path_defaults = os.path.join(path_root, f"Inputs/Coil Configurations/Defaults")
    path_DIR = os.path.join(path_root, f"Inputs/Coil Configurations")

    # TEST WIDGETS STARTING HERE
    test_dcls = CircleCurrentConfig # the class reference to the entry table's dataclass
    test_table = CurrentEntryTable(master=root_frame,
                                   dataclass=test_dcls,
                                   defaults=path_defaults,
                                   DIR=path_DIR,
                                   graphFrame=graph_frame)
    
    # packing
    root_frame.pack(expand=1, fill='both', anchor='center')
    graph_frame.pack()

    # RUN MAINLOOP
    root.mainloop()
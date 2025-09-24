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
# from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
# from system.temp_file_names import manager_1, m1f1
from settings.defaults.coils import default_coil, coil_cust_attr_name
from definitions import PLATFORM, NAME_COILS

from system.state_dict_main import AppConfig
from Gui_tkinter.widgets.base import ParamWidget

if PLATFORM != "win32":
    from xattr import setxattr
else:
    import os

from pathlib import Path


class EntryTable(ParamWidget):
    '''Display a csv with dynamically created rows.'''

    def GetEntries(self, csv=False):
        pass

    def __init__(self, master, data, rows=None):  # initialization function
        """
        Can initialize data in multiple ways:
            - data, rows (each as list)
            - data (as a dict containing both variable and data info)
        """
        if isinstance(data, dict):
            # dict case
            self.headers = list(data.keys())
            # zip values by column -> rows
            self.rows = list(zip(*data.values()))
        elif isinstance(data, list) and isinstance(rows, list):
            # headers + rows case
            self.headers = data
            self.rows = rows
        else:
            raise ValueError("Invalid input format: must be (headers, rows) or dict")



    def EntryValidateCallback(self, entry, check_float=True):
        '''
        Callback function that is called by entryboxes.

        When a user updates an entry box, call this function to:
            1. Validate entry type (not implemented here atm)
            2. Update its corresponding field in self.entries
        '''

    def DelEntry(self, button):
        '''
        Deletes its respective row of the entry table, as well as its data in self.entries.
        '''
        pass

    def NewEntry(self, *args, defaults=True):
        '''
        Creates a new row for the entry table


        if not creating a default row, you must pass an instance of a dataclass
        with the desired values.

        if called at the time of more than one row in the table, then just copies the row at the last index
        '''
        pass

    def ClearTable(self):
        '''
        deletes everything from the table. That means, everything
        except for the first row of the frame (which has the column information)
        '''
        pass

    def SetRows(self, list):
        '''
        given a list of dataclass objects, populate the table with respective rows.
        Expected to run when files are loaded. therefore, it clears the entry table.
        '''
        pass

    def _SetSaveEntry(self, name: str, **kwargs):
        '''
        whenever this is called, the save entry field gets filled with the currently selected file's name.


        Because this base class does not include the file dropdown, it's expected that the name parameter is filled
        by its children. Otherwise, this function will just go unused.
        '''
        pass

    def SaveData(self, dir: str, container=None, vals=None, customContainer=False):
        '''
        after reading where to save (DIR variable from somewhere),
        look at the value of the nearby entry widget and either create the file (if not present)
        or overwrite to the already existing file.

        format:
        1st line is the names of all the fields

        Every line following are values that fall under these fields.
        '''
        pass

    def GetData(self):
        '''
        when called, reads the currently held data points and outputs it in a readable format.


        self.entries is a list of dictionaries; each list entry is a row in the table.
        Therefore, the format could be: {key = "<entry name>_<n>" : value = <dataclass instance>}


        Or a nested dictionary. I'm going with nested dictionary. It's easy, and I'm stupid.
        '''
        pass

    def Read_Data(self, dir=None, eval_ind=None, dct=False, **kwargs):
        '''
        look at the dir of the selected input file, then turn it into rows on the entry table
        (param: ) dir: a string path to the input file to read. It defaults to None, so that just calling the function will read the currently selected value from the corresponding dropdown instead.
        '''
        pass

    def _NewFile(self, dir: str, name: str, data=None):
        '''
        helps the programmer from having to call the many functions associated with this
        functionality.
        '''
        pass

from enum import Enum
from functools import partial

from events.funcs import before_simulation_bob_dt, copy_diags_to_output_subdir, initialize_tempfile_dict
from files.checks import folder_checks, ini_checks
from system.temp_manager import TEMPMANAGER_MANAGER
import system.temp_file_names as names

from settings.configs.funcs.config_reader import read_configs
from settings.configs.funcs.configs import create_default_config

from files.create import get_output_subdir, create_output_file

"""
Definitions for all the different GUI user events (that exist at a higher level than tkinter's widgets)
"""

"""
An internal class for defining the functions to run when an event is called.
Basically a list containing callables with a function to call them.
"""
class Event():
    def __init__(self, callables:list):
        self.callables = callables
        #print(self.callables)
    
    """
    runs all the callables that the object is responsible for.
    """
    def invoke(self, **kwargs):
        for c in self.callables:
            c(**kwargs)

def _whatis_file():
    print(f"events._whatis_file()")
    print(TEMPMANAGER_MANAGER.files[names.m1f1])

"""
This is the big object that other scripts are pining for!

# OVERVIEW
An enum that essentially connects the event's name to a list of associated funcs to call when invoked.
Do note that the listed funcs may not contain ALL called functions, as objects can add more callables
to the list during runtime.

For example, a system.temp_manager.TempManager instance has a programmable termination event that appends
to the event's list.

# TO CALL AN EVENT:
1. import this enum 'from events.events import Events'
2. call: '<event_name>.invoke()'
"""
class Events(Enum):
    # as soon as app is run: checks and big managers
    ON_START = Event([
                      create_default_config, # create default .ini
                      read_configs, # get the runtime configs ConfigParser object
                      folder_checks, # check dir structure
                      ])
    
    # set up everything needed before widgets can be messed with
    PRE_INIT_GUI = Event([partial(TEMPMANAGER_MANAGER.add_temp_manager, names.manager_1),
                          partial(TEMPMANAGER_MANAGER.create_temp_file, names.manager_1, names.m1f1),
                          partial(TEMPMANAGER_MANAGER.create_temp_file, names.manager_1, names.m1f2), # holds png of trajectory
                          ])

    # after creating the tempfile(s), you can then fill widgets with the last used values.
    # this also functions to fill the tempfile with all of the expected fields (as every widget gets to update the tempfile)
    INIT_GUI = Event([initialize_tempfile_dict])

    # when calculate button is pressed but before the calcs start.
    PRE_CALC = Event([before_simulation_bob_dt, # set up constants if using bob's dt scaling solution
                      get_output_subdir, # creates subdirs according to path keys
                      copy_diags_to_output_subdir, # copy diagnostic files to them
                      create_output_file, # creates the default h5 file
                      ])

    # after a sim finishes
    POST_CALC = Event([])

    PRE_PLOT = Event([
                      ])

    # when the program terminates
    ON_CLOSE = Event([TEMPMANAGER_MANAGER.dump_params, 
                      TEMPMANAGER_MANAGER.del_all_temp])

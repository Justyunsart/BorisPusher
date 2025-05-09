from enum import Enum
from functools import partial

from events.funcs import before_simulation_bob_dt
from files.checks import folder_checks
from system.temp_manager import TEMPMANAGER_MANAGER
import system.temp_file_names as names


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
    def invoke(self):
        for c in self.callables:
            c()

def _whatis_file():
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
    ON_START = Event([folder_checks, # check dir structure
                      ])
    
    # set up everything needed before widgets can be messed with
    PRE_INIT_GUI = Event([partial(TEMPMANAGER_MANAGER.add_temp_manager, names.manager_1),
                          partial(TEMPMANAGER_MANAGER.create_temp_file, names.manager_1, names.m1f1)])
    
    INIT_GUI = Event([])

    # when calculate button is pressed but before the calcs start.
    PRE_CALC = Event([before_simulation_bob_dt,
                     ])

    # after a sim finishes
    POST_CALC = Event([])

    # when the program terminates
    ON_CLOSE = Event([TEMPMANAGER_MANAGER.del_all_temp])

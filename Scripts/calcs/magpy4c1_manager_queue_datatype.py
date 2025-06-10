from dataclasses import dataclass
"""
A custom class will be submitted to the manager queue between the backend and the GUI to facilitate
sending multiple labelled pieces of information.
"""
@dataclass
class Manager_Data():
    step:int = 0
    do_stop:bool = False
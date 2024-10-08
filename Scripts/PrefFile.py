'''
Stores the base class for the structure of the main preferences text file.
'''
from dataclasses import dataclass

# TODO: Make way to get, set these fields.
@dataclass
class PrefFile():
    DIR_particle:str
    DIR_coil:str
    DIR_output:str
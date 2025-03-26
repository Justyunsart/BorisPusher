'''
Stores the base class for the structure of the main preferences text file.

Also stores the base class for the structure of the previously used configs.
'''
from dataclasses import dataclass

@dataclass
class PrefFile():
    DIR_particle:str
    DIR_coil:str
    DIR_coilDefs:str
    DIR_Bob:str
    DIR_BobDefs:str

    DIR_output:str
    DIR_lastUsed:str

    PAR_dt:str
    PAR_numsteps:str

    PAR_B:str
    PAR_E:str

@dataclass
class PrevFiles():
    DIR_particle:str
    DIR_coil:str
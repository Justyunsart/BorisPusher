'''
Stores the base class for the structure of the main preferences text file.

Also stores the base class for the structure of the previously used configs.
'''
from dataclasses import dataclass

@dataclass
class PrefFile():
    """
    Container class for key program settings. There are these categories of attributes:
        DIRs: a string path to relevant folders.
        FILEs: a string path representing the location of a file.
        PARs: a string that represents different simulation parameter values.
    """
    # Input file DIRS
    DIR_particle:str
    DIR_coil:str
    DIR_coilDefs:str
    DIR_Bob:str
    DIR_BobDefs:str
    # Output file DIRS
    DIR_output:str
    FILE_lastUsed:str # PATH to the file containing info. for the previously used settings.

    # PARAMS
    PAR_dt:str
    PAR_numsteps:str
    PAR_B:str
    PAR_E:str
    
    @property
    def DIRS(self):
        return [self.DIR_particle, self.DIR_coil, self.DIR_coilDefs, self.DIR_Bob, self.DIR_BobDefs, self.DIR_output]
    @property
    def FILES(self):
        return [self.FILE_lastUsed]
    @property
    def PARS(self):
        return [self.PAR_dt, self.PAR_numsteps, self.PAR_B, self.PAR_E]

@dataclass
class PrevFiles():
    DIR_particle:str
    DIR_coil:str
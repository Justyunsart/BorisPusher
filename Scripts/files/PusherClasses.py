from definitions import DIR_ROOT, NAME_INPUTS, NAME_COILS, NAME_OUTPUTS
from settings.configs.funcs.config_reader import runtime_configs
from dataclasses import dataclass, asdict, field
import numpy as np

import pandas as pd
import shutil

import os

'''
What will the folder for each output be called?
     > Might be able to make this from a user input, otherwise will make a default name.

Default name: "boris_nsteps_nsecs_nparticles"

* when facing duplicate names, add (1), (2), etc.
     1 - attempt to create the dir with the name
     3 - except when an error comes from 1.
        3a - in case of an error, have the os list the outd contents, and use counter() to see the num of occurances of the duplicate name
        3b - make the new dir the name + (n) occurances 
    return the name
'''
def CreateOutDir(numsteps, numtime, numparts):
    outd = runtime_configs['Paths']["Outputs"]
    dName = "boris_" + str(numsteps) + "_" + str(numtime) + "_" + str(numparts)  
    path = os.path.join(outd, dName)
    
    counter = 0
    temp = ""
    while os.path.exists(path):
        counter += 1
        temp = f"{dName}_({counter})"
        path = os.path.join(outd, temp)

    os.makedirs(path)
    
    return path

#==================#
# CREATE DATAFRAME #
#==================#

'''
Make a large dataframe that aggregates the AoS to a more exploitable format. 
     > We have to do these conversions to utilize arrays' strength of O(1) lookup and adding, as well as to avoid excessive amendments to a dataframe (costly)

To keep track of particles, we will add an 'id' categorical variable alongside the usual 'particle' class attributes.
'''
def InitializeAoSDf(AoS:np.ndarray):
    flat = np.hstack(AoS)
    dfo = pd.json_normalize(asdict(i) for i in flat)

    return dfo

def CreateOutput(inp, sim_time, num_points, num_parts, part, bf, ef, c, diags):

    # MAKE NEW FILE FOR EACH PARTICLE
    # First, make the dir for these files.
    dir = CreateOutDir(numparts=num_parts, numsteps=num_points, numtime=sim_time)
    data = InitializeAoSDf(inp)

    # Next, create a new file for each particle
   #for i in range(df.shape[0]):
    #    temp = os.path.join(dir, f"{i}.txt")
        # print("saving, ", AoS[i])
        # np.save(temp, AoS[i])
    diag_path = os.path.join(dir, f"diagnostics.txt")
    diags.to_csv(diag_path)
    
    temp = os.path.join(dir, f"dataframe.json")
    data.to_json(temp, orient="table")

    particles = os.path.join(dir, f"particles.txt")
    part.to_json(particles, orient="table")

    fields_dir = os.path.join(dir, f"fields.txt")
    fields = {"B" : bf,
              "E" : ef}
    fields = pd.DataFrame.from_dict(fields, orient="index")
    fields.to_csv(fields_dir, header=False)

    coil_dir = os.path.join(dir, f"coils.txt")
    coil_file = open(coil_dir, "w")
    file_to_copy = os.path.join(os.path.join(DIR_ROOT, f"{NAME_INPUTS}/{NAME_COILS}"), c)

    shutil.copy(file_to_copy, coil_dir)

    coil_file.close()

    return temp


#===========#
# Dataclass #
#===========#

'''
The struct-like data class that will be stored inside an array (Array of structs data structure, or AoS)
Makes the data, code more intuitive.

I made the pos, vel, and b fields separate floats because pandas really hates it when cells are containers; doing any manipulation of data
was causing me immense agony and pain. It makes particle instantiation really ugly... Too bad!
'''
@dataclass
class particle:
    id: int
    step: int
    
    #position
    px: np.float64 = None
    py: np.float64 = None
    pz: np.float64 = None

    # Velocity
    vx: np.float64 = None
    vy: np.float64 = None
    vz: np.float64 = None

    # B field
    bx: np.float64 = None
    by: np.float64 = None
    bz: np.float64 = None

    # E field
    ex: np.float64 = None
    ey: np.float64 = None
    ez: np.float64 = None

    # Diags
    vperp: np.float64 = None
    vpar: np.float64 = None
    vmag: np.float64 = None

    eperp: np.float64 = None
    epar: np.float64 = None
    emag: np.float64 = None

    bmag: np.float64 = None
    bhx: np.float64 = None
    bhy: np.float64 = None
    bhz: np.float64 = None

@dataclass
class charge:
    position: np.ndarray
    q: float

def UniqueFileName(DIR, fileName:str):
    '''
    given a path to a file and filename, return either the fileName (if unique)
    or fileName(n) if not.
    '''
    parent = DIR
    counter = 0
    temp = fileName
    while os.path.exists(os.path.join(parent, temp)):
        counter += 1
        temp = f"{fileName}({counter})"
    return temp

###############################################################################
# custom np.dtype so that the hdf5 output file datasets will have column names.
position_dt = np.dtype([('px', np.float64), ('py', np.float64), ('pz', np.float64)])
velocity_dt = np.dtype([('vx', np.float64), ('vy', np.float64), ('vz', np.float64), ('vperp', np.float64), ('vpar', np.float64), ('vmag', np.float64)])
field_b_dt = np.dtype([('bx', np.float64), ('by', np.float64), ('bz', np.float64), ('bmag', np.float64), ('bhx', np.float64), ('bhy', np.float64), ('bhz', np.float64)])
field_e_dt = np.dtype([('ex', np.float64), ('ey', np.float64), ('ez', np.float64), ('eperp', np.float64), ('epar', np.float64), ('emag', np.float64)])
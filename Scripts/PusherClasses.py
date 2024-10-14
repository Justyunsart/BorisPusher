# Global classes and structures that many scripts rely on.
# Made to streamline coupling

from dataclasses import dataclass, asdict
from magpylib import Collection
import numpy as np

from math import pi, cos, sin

import pandas as pd

from pathlib import Path
import os
# gui stuff
cwd = str(Path(__file__).resolve().parents[1]) # Gets the current working directory, so we can find the Inputs, Outputs folder easily.
outd = cwd + "/Outputs"

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
    global outd
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

'''
From the GUI: 
1. Determine if we're reading input data or not.
2. Populate the dataframe accordingly.

For each dataframe row:
1. Create a Particle object
2. Apply the data from the input file to its fields
3. Store the Particle object in an array

Magpy integration:
1. Create a magpy.collection of magpy.sensors corresponding to each particle
    > The index of each sensor will correspond to the index of the particle

IMPORTANT:
    > Whether we read input data or not comes from the 'do_file' var from the GUI.
    > The dataframe is a table of Particle classes.
        - row # = particle index
        - column = attribute
    > 'inpd' is set whenever the input file dir is updated, to the file's dir.
'''
def InitializeData(do_file: bool, inpd:str):

    if(do_file == False):
        data = pd.read_csv(cwd + "/Inputs/Default_Input.txt", dtype = {"positions" : str, "vels" : str, "accels" : str})
    else:
        inp = inpd
        if(inp != ""):
            data = pd.read_csv(inp, dtype = {"positions" : str, "vels" : str, "accels" : str})
        else:
            print("path not found")
    # CLEANING

    # Convert columns to Arrays
    data["starting_pos"] = data["starting_pos"].str.split(" ").apply(pd.to_numeric, errors = "coerce")
    data["starting_vel"] = data["starting_vel"].str.split(" ").apply(pd.to_numeric, errors = "coerce")

    # print(data["starting_pos"])
    return data


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

def CreateOutput(inp, sim_time, num_points, num_parts):
    global outd

    # MAKE NEW FILE FOR EACH PARTICLE
    # First, make the dir for these files.
    dir = CreateOutDir(numparts=num_parts, numsteps=num_points, numtime=sim_time)
    data = InitializeAoSDf(inp)

    # Next, create a new file for each particle
   #for i in range(df.shape[0]):
    #    temp = os.path.join(dir, f"{i}.txt")
        # print("saving, ", AoS[i])
        # np.save(temp, AoS[i])

    temp = os.path.join(dir, f"dataframe.json")
    data.to_json(temp, orient="table")


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
    px: np.float64
    py: np.float64
    pz: np.float64

    # Velocity
    vx: np.float64
    vy: np.float64
    vz: np.float64

    # B field
    bx: np.float64
    by: np.float64
    bz: np.float64

@dataclass
class charge:
    position: np.ndarray
    q: float

#========#
# Fields #
#========#
EfOptions = np.array(["Zero", "Static", "Calculated"])
BfOptions = np.array(["Zero", "Static", "Calculated"])


def GetCurrentTrace(c:Collection, dia:int, res:int, nsteps:int):
    '''
    Gets the positional coordinates for points to estimate the circular plane when doing point charge calculations.

    c: the magpy collection object that contains only circular traces
    dia: the traces' diameter
    res: the resolution of the trace for each circle (higher = more points; the better the circle gets simulated)
    nsteps: the number of evenly spaced circles placed on the surface

    Returns an array containing all the coordinates
    '''
    rad = dia/2
    rads = np.linspace(0, rad, nsteps)
    # need to figure out what axis the slices are
    orientations = []
    points = []
    for current in c.children:
        # Find the direction the circle is facing, for science.
        orientation = current.orientation.as_euler('xyz', degrees=True)
        orientations.append(orientation)

        # Find the interval to plug into the circle formula.
        axis = np.where(orientation > 0) # shows where the circle is facing??
        
        # set local x and y axes (these are indexes of 0 = x, 1 = y, 2 = z)
        if axis[0] == 2:
            xl = 1
            yl = 0
            zl = 2
        elif axis[0] == 0:
            xl = axis[0]
            yl = 2
            zl = 1
        else:
            xl = 1
            yl = 2
            zl = 0

        center = current.position # centerpoint of circle
        #print(center)

        theta = 0
        dtheta = 2*pi/res
        while theta <2*pi:
            p1 = np.array([cos(theta), sin(theta), 0]) # generic circle
            p1arr = np.array(list(map(lambda x: np.multiply(x, p1, dtype=float), rads))).T
            #print(p1arr)
            #p1 = np.multiply(rads, p1).T # circle with the trace's radius

            # adjustments for the local x, y, z vars (based on orientation)
            p2 = np.zeros((3, nsteps))
            p2[xl] = p1arr[0]
            p2[yl] = p1arr[1]
            p2[zl] = p1arr[2]

            p2 = p2.T
            #print(p2.shape)
            p2 += center # move to circle's centers
            points.append(p2)

            theta += dtheta #increment circle angle
    
    points = np.asarray(points)

    return points

def GetDistSq(v1:np.ndarray, v2:np.ndarray):
    '''
    v1: an iterable with n, 3 shape, representing n observer coords
    v2: an iterable container with len 3 representing coords
    '''
    shape = list(np.shape(v1))
    v1 = np.array(v1.reshape((shape[0] * shape[1], 3)))
    #print(v1)
    #print(v2)

    difference = np.array(v1 - v2)
    differencesq = np.power(difference, 2)
    #differencesq = np.sum(differencesq, axis=1)
    #print(np.shape(differencesq))
    #distsq = (v2[0] - v1[0])**2 + (v2[1] - v1[1])**2 + (v2[2] - v1[2])**2
    #distsq = np.sum(differencesq, axis=1)
    #print(differencesq)
    #print(v1[0], " of shape: ", np.shape(v1[0]))
    #print(v2)
    #print(v1[0], " minus", v2, " is: ", v1[0] - v2)
    return(np.zeros(3))

def CalcPtE(obs:np.ndarray, pt:np.ndarray, q:float):
    '''
    obs: container with n, 3 shape representing the coords of all observers
    pt: container with 3 shape representing the coords of the point to calculate at
    q: the charge to calculate E with
    '''
    k = 8.99 * 10.0**9 #electrostatic constant

    distances = GetDistSq(obs, pt)
    E = np.multiply((np.divide(abs(q), distances)), k)
    E1 = np.sum(E, axis=0)
    print(E1)
    return E1

class Config():
    '''
    Contains all information used in the simulation. Used to keep track of the parameters used for each dataframe,
    as well as knowing the previously used configuration.

    Info to track:
        - path to initial conditions file
        - Numsteps
        - Sim Time
        - Coil setup
    '''

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
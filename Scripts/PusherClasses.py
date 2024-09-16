# Global classes and structures that many scripts rely on.
# Made to streamline coupling

from dataclasses import dataclass, asdict
from magpylib.current import Circle as C
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

#=========#
# Current #
#=========#
# creates a square box of Loop coils
def Circle(a, dia, d, gap):
    # current Loop creation, superimpose Loops and their fields
    s1 = C(current=a, diameter=dia).move([-(d/2)-gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s2 = C(current=-a, diameter=dia).move([(d/2)+gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s3 = C(current=-a, diameter=dia).move([0,-(d/2)-gap,0]).rotate_from_angax(90, [1, 0, 0])
    s4 = C(current=a, diameter=dia).move([0,(d/2)+gap,0]).rotate_from_angax(90, [1, 0, 0])
    s5 = C(current=a, diameter=dia).move([0,0,-(d/2)-gap]).rotate_from_angax(90, [0, 0, 1])
    s6 = C(current=-a, diameter=dia).move([0,0,(d/2)+gap]).rotate_from_angax(90, [0, 0, 1])

    c = Collection(s1,s2,s3,s4,s5,s6, style_color='black')
    return c


# helmholtz setup for a test
def Helmholtz(a, dia, d):
    # helmholtz test
    s7 = C(current=a, diameter=dia).move([-(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])
    s8 = C(current=a, diameter=dia).move([(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])

    c = Collection (s7, s8)
    return c

def GetCurrentTrace(c:Collection, dia:int, res:int):
    rad = dia/2
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

        theta = 0
        dtheta = 2*pi/res
        while theta <2*pi:
            p1 = np.array([cos(theta), sin(theta), 0]) # generic circle
            p1 = (p1 * rad) # circle with the trace's radius

            # adjustments for the local x, y, z vars (based on orientation)
            p2 = np.zeros(3)
            p2[xl] = p1[0]
            p2[yl] = p1[1]
            p2[zl] = p1[2]

            p2 += center # move to circle's centers
            #p3 = charge(position= np.array(p2), q=current.current)
            points.append(p2)

            theta += dtheta #increment circle angle
    
    points = np.asarray(points)

    return points

def GetDistSq(v1, v2):
    '''
    v1: an iterable with n, 3 shape, representing n observer coords
    v2: an iterable container with len 3 representing coords
    '''
    difference = v1 - v2
    differencesq = np.power(difference, 2)
    #distsq = (v2[0] - v1[0])**2 + (v2[1] - v1[1])**2 + (v2[2] - v1[2])**2
    #distsq = np.sum(differencesq, axis=1)
    return(differencesq)

def CalcPtE(obs, pt, q:float):
    '''
    obs: container with n, 3 shape representing the coords of all observers
    pt: container with 3 shape representing the coords of the point to calculate at
    q: the charge to calculate E with
    '''
    k = 8.99 * 10^9 #electrostatic constant

    distances = GetDistSq(obs, pt)
    E = np.multiply((np.divide(abs(q), distances)), k)
    E1 = np.sum(E, axis=0)

    print(E1)
    return E1
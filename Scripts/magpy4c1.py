##########################################################################
# BORIS PUSHER, UX FLOW                                                  #
#     - Calls functions from other scripts to construct the Boris push   #
# Andrew Egly, Yoon Roh, Bob Terry                                       #
##########################################################################

# get particle's angular momentum along the gyroradius. components of p (perpen to magnetic vector) cross w/ r gives axial direction.
#     > angular momentum along the field line. 


from dataclasses import dataclass, asdict

import numpy as np
import magpylib as magpy
import os

# parallelization
import ray
# ray.init()

# used to create output restart file
import pandas as pd

# gui stuff
from BorisGui import root, do_file, inpd, entry_numsteps_value, time_step_value, entry_sim_time_value
# magpy and plots
from magpylib.current import Loop
from magpylib import Collection

# please dont truncate anything
pd.set_option('display.max_columns', None)
# Run GUI loop
root.mainloop()

###################
# INPUT FILE JUNK #
###################
#======#
# VARS #
#======#

initialized = False # Ensure initialization only happens once : failsafe
cwd = os.getcwd() # Gets the current working directory, so we can find the Inputs, Outputs folder easily.
outd = cwd + "/Outputs" 

#=================================#
# HELPERS FOR READING INPUT FILES #
#=================================#
def StrToArr(text):
    return np.fromstring(text, sep = ' ')

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

def InitializeData():
    global initialized
    global simDf
    # Making sure initialization only happens once
    assert initialized == False
    initialized = True

    if(do_file.get() == False):
        data = pd.read_csv(cwd + "/Inputs/Default_Input.txt", dtype = {"positions" : str, "vels" : str, "accels" : str})
    else:
        data = pd.read_csv(inpd, dtype = {"positions" : str, "vels" : str, "accels" : str})
    
    # CLEANING

    # Convert columns to Arrays
    data["starting_pos"] = data["starting_pos"].str.split(" ").apply(pd.to_numeric, errors = "coerce")
    data["starting_vel"] = data["starting_vel"].str.split(" ").apply(pd.to_numeric, errors = "coerce")

    # print(data["starting_pos"])
    return data

df = InitializeData() # Populate this ASAP lol

'''
Creates the output file
'''
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
    df = pd.json_normalize(asdict(i) for i in flat)

    return df

def CreateOutput():
    global outd

    # MAKE NEW FILE FOR EACH PARTICLE
    # First, make the dir for these files.
    dir = CreateOutDir()
    df = InitializeAoSDf(AoS)

    # Next, create a new file for each particle
   #for i in range(df.shape[0]):
    #    temp = os.path.join(dir, f"{i}.txt")
        # print("saving, ", AoS[i])
        # np.save(temp, AoS[i])

    temp = os.path.join(dir, f"dataframe.json")
    df.to_json(temp, orient="table")
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
def CreateOutDir():
    global outd
    dName = "boris_" + str(entry_numsteps_value.get()) + "_" + str(entry_sim_time_value.get()) + "_" + str(df.shape[0])  
    path = os.path.join(outd, dName)
    
    counter = 0
    temp = ""
    while os.path.exists(path):
        counter += 1
        temp = f"{dName}_({counter})"
        path = os.path.join(outd, temp)

    os.makedirs(path)
    
    return path


####################
# PHYSICS SETTINGS #
####################

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

# preallocate the array in memory
AoS = np.empty(dtype=particle, shape=((df.shape[0], entry_numsteps_value.get() + 1)))  # there will be {(numsteps + 1), numparticles} entries, with one added to account for initial conditions.

#=========#
# Current #
#=========#
# creates a square box of Loop coils
def Circle(a, dia, d, gap):
    # current Loop creation, superimpose Loops and their fields
    s1 = Loop(current=a, diameter=dia).move([-(d/2)-gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s2 = Loop(current=-a, diameter=dia).move([(d/2)+gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s3 = Loop(current=-a, diameter=dia).move([0,-(d/2)-gap,0]).rotate_from_angax(90, [1, 0, 0])
    s4 = Loop(current=a, diameter=dia).move([0,(d/2)+gap,0]).rotate_from_angax(90, [1, 0, 0])
    s5 = Loop(current=a, diameter=dia).move([0,0,-(d/2)-gap]).rotate_from_angax(90, [0, 0, 1])
    s6 = Loop(current=-a, diameter=dia).move([0,0,(d/2)+gap]).rotate_from_angax(90, [0, 0, 1])

    c = Collection(s1,s2,s3,s4,s5,s6, style_color='black')
    return c


# helmholtz setup for a test
def Helmholtz(a, dia, d):
    # helmholtz test
    s7 = Loop(current=a, diameter=dia).move([-(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])
    s8 = Loop(current=a, diameter=dia).move([(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])

    c = Collection (s7, s8)
    return c

#=========#
# B FIELD #
#=========#
'''
TODO:
- Make this work on an entire nested array instead of one array at a time.
- Possible multithreading?
Input: Array of (nparticle x pos(3)) dim
Output: Array of (nparticle x bf(3)) dim

Ensure the code is efficient because the whole point of these operations is to increase computational speed
'''

# using magpylib, this calculates the b-field affecting the particle
# unless it is outside of the bounds given by 'side'
def Bfield(y):
    out = []

    isBounds = y.any() > side
    Bf = [0.,0.,0.]
    if(not isBounds):
        Bf = c.getB(y, squeeze=True)
        out = Bf
    return np.array(out)

# global variables
magpy.graphics.style.CurrentStyle(arrow=None)
accel = None

# physics variables
a = 1.0e5 # current
aa = a / 1.72 # triangle current
dia = 500. # coil diameter
d = 800. # coil placement
l = 600 # line space(x, y, z variables)
r = 100 # line space increments

# plotting variables
corner = 1 # sets octagonal corner size (cannot be 0)
side = 600 # max range for plot
gap = 15 # sets space between coils
coilLength = 1000
dt = time_step_value

# comment in coils array you wish to use from the above definitions
# c = Helmholtz(a, dia, d)
c = Circle(a, dia, d, gap)



# boris push calculation
# this is used to move the particle in a way that simulates movement from a magnetic field
# mass and charge are set to 1, and input as 'm' and 'q' respectively
# @ray.remote
def borisPush(num_points, dt):
    global AoS
    global side
    global df

    num_parts = df.shape[0] # the number of particles in the simulation

    mass = 1.67e-27
    charge = 1.602e-19
    vAc = 1
    mm = 0.001
    ft = 0 

    # Step 1: populate AoS (Array of Structures) with initial conditions
    #     > These conditions are read from inp file, currently stored in df.
    for i in range(num_parts):
        temp = df["starting_pos"].to_numpy()[i]
        temp1 = df["starting_vel"].to_numpy()[i] * mm
        AoS[i][0] = particle(px = temp[0], 
                             py = temp[1],
                             pz = temp[2],
                             vx = temp1[0],
                             vy = temp1[1],
                             vz = temp1[2],
                             bx = 0,
                             by = 0,
                             bz = 0,
                             id = i,
                             step = 0)


    E = np.array([0., 0., 0.])

    # Step 2: do the actual boris logic
    for time in range(num_points): # time: step number
        for i in range(num_parts): # i: particle index
            # AoS is actually an AoAoS (Array of Array of Structs)
            #     > AoS[i]: particle id's own array
            #   /  > AoS[i][time]: particle 'i' at step 'time'

            x = np.array([AoS[i][time].px, AoS[i][time].py, AoS[i][time].pz])
            v = np.array([AoS[i][time].vx, AoS[i][time].vy, AoS[i][time].vz])

            Bf = Bfield(x)
            AoS[i][time].bx, AoS[i][time].by, AoS[i][time].bz = Bf # update B field for particle we just found

            # Boris logic
            tt = charge / mass * Bf * 0.5 * dt
            ss = 2. * tt / (1. + tt * tt)
            v_minus = v + charge / (mass * vAc) * E * 0.5 * dt
            v_prime = v_minus + np.cross(v_minus, tt)
            v_plus = v_minus + np.cross(v_prime, ss)

            # Update particle information with the pos and vel
            position = x + v * dt 
            velocity = v_plus + charge / (mass * vAc) * E * 0.5 * dt
            AoS[i][time + 1] = particle(px = position[0], 
                             py = position[1],
                             pz = position[2],
                             vx = velocity[0],
                             vy = velocity[1],
                             vz = velocity[2],
                             bx = 0,
                             by = 0,
                             bz = 0,
                             id = i,
                             step = time)

        ft += dt # total time spent simulating
        if time % 1000 == 0:
            print("boris calc * " + str(time))
            print("total time: ", ft, dt)
        if x.any() > side:
            print('Exited Boris Push Early')
            break
    print(ft*(10**-5))
    ft = ft*(10**-5)

#calc = True
# if(calc):       
#     future = borisPush.remote(entry_numsteps_value.get(), time_step_value)
#     result = ray.get(future)
#     CreateOutput()
# ray.shutdown()

calc = True
if(calc):
    borisPush(entry_numsteps_value.get(), time_step_value)
    CreateOutput()
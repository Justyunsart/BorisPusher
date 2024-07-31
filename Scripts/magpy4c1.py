from collections import namedtuple
from dataclasses import dataclass

import math
import time
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import magpylib as magpy
import os

# parallelization
import ray
# ray.init()

# used to create output restart file
import pandas as pd

# gui stuff
import tkinter
from BorisGui import root, do_file, inpd, entry_numsteps_value, time_step_value

# magpy and plots
from magpylib.current import Loop
from magpylib import Collection
from matplotlib import ticker
from matplotlib.colors import Normalize
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

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

'''
Functions access it directly
'''
df = InitializeData() # Populate this ASAP lol

'''
Prints out the resulting dataframe from the InitializeData() to debug
'''
def TestInitialization():  
    print(f"Dataframe: {df}")

'''
Creates the output file
'''
def CreateOutput():
    global outd

    Df = pd.DataFrame(AoS)
    Df.to_csv(outd + "/out3.txt", index = False, header = False)


## Uncomment below to check if the dataframe is being set properly.
# TestInitialization()

####################
# PHYSICS SETTINGS #
####################

#===========#
# Dataclass #
#===========#
'''
The struct-like data class that will be stored inside an array (Array of structs data structure, or AoS)
'''
@dataclass
class particle:
    position: np.ndarray
    velocity: np.ndarray
    B: np.ndarray

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
        out.append(Bf)
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
VelX = 5.8e5 # velocity in the 'X' direction for the particle In mm/s
VelY = VelX # velocity in the 'Y' direction for the particle In mm/s
VelZ = 0.0 # velocity in the 'Z' direction for the particle In mm/s
t1 = -10.
t2 = -10.

######################
# DEFAULT PARAMETERS #
######################
'''
If some elements in the GUI are not populated, the sim will use these conditions.
'''

# the initial starting point and velocity vectors in a list
yNot = np.array([[0., 0., 120., VelX/1.5, VelY, VelZ],
                 [0., 0.,-120., -VelX, VelY/1.5, VelZ],
                 [0., 0., 0., -VelX, -VelY, VelZ],
                 [0., 0., 0., -VelX, VelY, -VelZ],
                 [0., 0., 0., VelX, -VelY, -VelZ],
                 [0., 0., 0., -VelX, -VelY, -VelZ]])

# E = np.array([0.0, 0.0, 0.0])  # Volts/m
# B = [18000, 0, 0]
s,t = 450,30

# plotting variables
step = 50 # vector density
smLine = 1
edge = 125 # sets square coil length
limS = 600 # vector graph area
print(limS)

# setting limit space to cancel calculations outside of it
x_lim = (-limS, limS)
y_lim = (-limS, limS)
z_lim = (-limS, limS)
radi = 200
plot_pick = None

corner = 1 # sets octagonal corner size (cannot be 0)
side = limS # max range for plot
gap = 15 # sets space between coils
coilLength = 1000
# dt = coilLength / (math.sqrt(VelX**2 + VelY**2 + VelZ**2) * num_points)
dt = time_step_value


# comment in coils array you wish to use from the above definitions
# c = Helmholtz(a, dia, d)
c = Circle(a, dia, d, gap)



# boris push calculation
# this is used to move the particle in a way that simulates movement from a magnetic field
# mass and charge are set to 1, and input as 'm' and 'q' respectively
# @ray.remote
def borisPush(num_points, dt):
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
        AoS[i][0] = particle(position = df["starting_pos"].to_numpy()[i] * mm, velocity = df["starting_vel"].to_numpy()[i], B = [0,0,0])


    E = np.array([0., 0., 0.])

    # Step 2: do the actual boris logic
    for time in range(num_points): # time: step number
        for i in range(num_parts): # i: particle index
            # AoS is actually an AoAoS (Array of Array of Structs)
            #     > AoS[i]: particle id's own array
            #     > AoS[i][time]: particle 'i' at step 'time'

            x = AoS[i][time].position
            v = AoS[i][time].velocity

            Bf = Bfield(x)
            AoS[i][time].B = Bf # update B field for particle we just found

            # Boris logic
            tt = charge / mass * Bf * 0.5 * dt
            ss = 2. * tt / (1. + tt * tt)
            v_minus = v + charge / (mass * vAc) * E * 0.5 * dt
            v_prime = v_minus + np.cross(v_minus, tt)
            v_plus = v_minus + np.cross(v_prime, ss)

            # Update particle information with the pos and vel
            AoS[i][time + 1] = particle(position = x + v * dt, velocity = v_plus + charge / (mass * vAc) * E * 0.5 * dt, B = [0,0,0])

        # creating a gradient of resolution based on the acceleration and velocity for dt
        # vel = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        # accelVec = (v_plus - v_minus) / dt
        # accel = math.sqrt(accelVec[0]**2 + accelVec[1]**2 + accelVec[2]**2)
        
        # print(x[0])
        # accelList = np.append(accelList, [[accelVec[0], accelVec[1], accelVec[2], accel]], axis=0)

        ft += dt # total time spent simulating
        if time % 1000 == 0:
            print("boris calc * " + str(time))
            print("total time: ", ft, dt)
        if x.any() > side:
            print('Exited Boris Push Early')
            CreateOutput()
            break
    print(ft*(10**-5))
    ft = ft*(10**-5)
    CreateOutput()

        
borisPush(entry_numsteps_value.get(), time_step_value)
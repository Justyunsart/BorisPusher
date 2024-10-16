##########################################################################
# BORIS PUSHER                                                           #
#     - Calls functions from other scripts to construct the Boris push   #
# Andrew Egly, Yoon Roh, Bob Terry                                       #
##########################################################################

# parallelization
from concurrent.futures import ProcessPoolExecutor #multiprocessing

# used to create output restart file
import pandas as pd

# Pusher specific stuff
## Currents, dataclasses
from PusherClasses import particle
from PusherClasses import GetCurrentTrace, CreateOutput, CalcPtE
from MakeCurrent import dia, A, Bx
## Calculations
import numpy as np
import magpylib as magpy

from BorisPlots import graph_trajectory

# please dont truncate anything
pd.set_option('display.max_columns', None)

'''
global vars

staticB:int = 0
staticE:int = 0
B:list = []
E:list = []
'''


####################
# PHYSICS SETTINGS #
####################
#=========#
# B FIELD #
#=========#
'''
TODO:
- Make this work on an entire nested array instead of one array at a time.
- Possible multithreading?
Input: Array of (nparticle x pos(3)) dim

Ensure the code is efficient because the whole point of these operations is to increase computational speed
'''

# using magpylib, this calculates the b-field affecting the particle
# unless it is outside of the bounds given by 'side'
def Bfield(y):
    if staticB == 1:
        return B

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

#=========#
# E FIELD #
#=========#

'''
Calculates the E Field at point 'p' from the list of charge source coordinates given.
'''
def EfieldX(p:np.ndarray):
    if staticE == 1:
        return E
    E = np.multiply(A * np.exp(-(p[0] / Bx)** 4), (p[0]/Bx)**15)
    return np.array([E,0,0])

'''
# plotting variables
corner = 1 # sets octagonal corner size (cannot be 0)
side = 600 # max range for plot
gap = 15 # sets space between coils
coilLength = 1000
'''


# boris push calculation
# this is used to move the particle in a way that simulates movement from a magnetic field
def borisPush(id:int):
    global df, num_parts, num_points, dt, sim_time, side, staticB, staticE, B, E # Should be fine in multiprocessing because these values are only read,,,
    assert id <= (num_parts - 1), f"Input parameter 'id' received a value greater than the number of particles, {num_parts}"

    #print(df)
    mass = 1.67e-27
    charge = 1.602e-19

    vAc = 1
    #mm = 0.001
    ft = 0 # tracker for total simulation time

    # Step 1: Create the AoS the process will work with
    #     > These conditions are read from inp file, currently stored in df.

    out = np.empty(shape = (num_points + 1), dtype=particle) # Empty np.ndarray with enough room for all the simulation data, and initial conditions.

    #temp = df["starting_pos"].to_numpy()[id] # Populate it with the initial conditions at index 0.
    #temp1 = df["starting_vel"].to_numpy()[id] * 6

    row = df.iloc[id]
    starting_pos = [row["px"], row["py"], row["pz"]]
    starting_pos = [float(item) for item in starting_pos]
    starting_vel = [row['vx'], row['vy'], row['vz']]
    starting_vel = [float(item) for item in starting_vel]
    out[0] = particle(px = starting_pos[0], 
                            py = starting_pos[1],
                            pz = starting_pos[2],
                            vx = starting_vel[0],
                            vy = starting_vel[1],
                            vz = starting_vel[2],
                            bx = 0,
                            by = 0,
                            bz = 0,
                            id = id,
                            step = 0)


    #E = np.array([-9.5e5, 0., 0])
    E = np.array([0, 0., 0])
    #Bf = np.array([0., 0., 1])

    # Step 2: do the actual boris logic
    for time in range(1, num_points + 1): # time: step number
        x = np.array([out[time - 1].px, out[time - 1].py, out[time - 1].pz])
        v = np.array([out[time - 1].vx, out[time - 1].vy, out[time - 1].vz])
        #print("x for particle: ", id, " at time ", time, ": ", x)
        E = EfieldX(x)
        Bf = Bfield(x)
        #Bf = np.array([0.0, 0.0, 1])
        out[time - 1].bx, out[time - 1].by,out[time - 1].bz = Bf # update B field for particle we just found

        # Boris logic
        tt = charge / mass * Bf * 0.5 * dt
        ss = 2. * tt / (1. + tt * tt)
        v_minus = v + charge / (mass * vAc) * E * 0.5 * dt
        v_prime = v_minus + np.cross(v_minus, tt)
        v_plus = v_minus + np.cross(v_prime, ss)
        v = v_plus + charge / (mass) * E * 0.5 * dt

        # Update particle information with the pos and vel
        position = x + v * dt 
        # velocity = v_plus + charge / (mass * vAc) * E * 0.5 * dt
        out[time] = particle(px = position[0], 
                            py = position[1],
                            pz = position[2],
                            vx = v[0],
                            vy = v[1],
                            vz = v[2],
                            bx = 0,
                            by = 0,
                            bz = 0,
                            id = id,
                            step = time)

        ft += dt # total time spent simulating
        if time % 1000 == 0:
            print(f"boris calc * {time} for particle {id}")
            print("total time: ", ft, dt, E)
        if x.any() > side:
            print('Exited Boris Push Early')
            break
    # ft = ft*(10**-5)
    return out

def init_process(data, n1, n2, t, t1, doB, doE, Bf, Ef, coils):
    global df, num_parts, num_points, dt, sim_time, side, staticB, staticE, B, E, c
    df = data
    num_parts = n1
    num_points = n2
    dt = t
    sim_time = t1
    #sources = GetCurrentTrace(c, dia, res=100, nsteps=100)
    side=3

    staticB = doB
    staticE = doE
    B = np.array(Bf)
    E = np.array(Ef)

    c = coils

    #print("data shared: ", data, n1, n2, t)

def runsim(fromGui:dict):
    dfIn = pd.DataFrame(fromGui['particles'])
    numPa = dfIn.shape[0]
    numPo = int(fromGui['numsteps'])
    tScale = fromGui['timestep']
    time = numPo * tScale
    doB = fromGui['doStaticB']
    doE = fromGui['doStaticE']
    Bf = fromGui['B-Field']
    Ef = fromGui['E-Field']
    coils = fromGui['coils']

    init_process(dfIn, numPa, numPo, tScale, time, doB, doE, Bf, Ef, coils)
    values = range(numPa)
    with ProcessPoolExecutor(initializer=init_process, initargs=(dfIn, numPa, numPo, tScale, time, doB, doE, Bf, Ef, coils)) as executor:
        futures = executor.map(borisPush, values)

    out = []
    for future in futures:
        out.append(future)

    out = np.asarray(out)

    dir = CreateOutput(out, sim_time, num_points, num_parts)
    graph_trajectory(lim=side, data=dir)

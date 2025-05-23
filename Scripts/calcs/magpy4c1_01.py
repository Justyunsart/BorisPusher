##########################################################################
# BORIS PUSHER                                                           #
#     - Calls functions from other scripts to construct the Boris push   #
# Andrew Egly, Yoon Roh, Bob Terry                                       #
##########################################################################

# parallelization
from concurrent.futures import ThreadPoolExecutor #multithreading
from concurrent.futures import ProcessPoolExecutor #multiprocessing

# used to create output restart file
import pandas as pd

# Pusher specific stuff
## Currents, dataclasses
from files.PusherClasses import particle
from files.PusherClasses import CreateOutput
## Calculations
import numpy as np
import magpylib as magpy

## Computation Diagnostics
import time as t

# Field Methods
from settings.fields.FieldMethods_Impl import (bob_e_impl)

# Linalg stuff
from Alg.polarSpace import toCart, toCyl

# Constants
from Scripts.settings.constants import proton

from calcs.bob_dt import bob_dt_step

from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict
from system.temp_file_names import m1f1

# please dont truncate anything
pd.set_option('display.max_columns', None)

####################
# PHYSICS SETTINGS #
####################
#=========#
# B FIELD #
#=========#

# unless it is outside of the bounds given by 'side'
def Bfield(y):
    global B_Method, c
    if(B_Method == "Zero"):
        return np.zeros(3)

    Bf = c.getB(y, squeeze=True)
    return np.array(Bf)

# global variables
magpy.graphics.style.CurrentStyle(arrow=None)
accel = None

#=========#
# E FIELD #
#=========#
"""
Extra wrapper functions to gather inputs to plug into the implementation.
"""
def Fw(coord:float):
    """
    Fw analytic E field equation
    """
    global E_Args
    A = float(E_Args["A"])
    Bx = float(E_Args["B"])
    #print(f"coord: {coord}, A: {A}, B: {Bx}")
    return np.multiply(A * np.exp(-(coord / Bx)** 4), (coord/Bx)**15)

def _Bob_e(inCoord, c):
    """
    The internal function passed to each thread in Bob_e().

    Inputs:
    inCord: the coordinate of the point to calculate E at.
    cnr: the coordinate of the circle's center and its radius.
    """

    global E_Args
    q = c.current # charge
    #print(f"running with the q:{q}")
    res = float(E_Args["res"]) # amount of points to be used in the integration
    
    # To make the target point relative to the coil, we call the bob_e.impl's alignment func.
    normCoord = bob_e_impl.OrientPoint(c=c, point=inCoord)
    radius = c.diameter / 2

    # Then pass this as the coordinate parameter of the implementation.
    z, r = bob_e_impl.at(coord = normCoord, q=q, resolution=int(res), radius= radius, convert=False)

    return z, r

def Bob_e(coord):
    global c_cnr, c    
    """
    This function will utlize multithreading, with each coil
    calculating its own e-field on a new thread.
    """
    zetas = []
    rhos = []
    cyl_coord = toCyl(coord)
    E_collection = E_Args['collection']
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_Bob_e, cyl_coord, coil): coil for coil in E_collection}

        # Gather the data from futures once completed.
        for index, task in enumerate(futures):
            result = task.result()
            zetas.append(result[0])
            rhos.append(result[1])
        z_sum = sum(zetas)
        r_sum = sum(rhos)
        # since the ring e field is rotationally symmetrical, the theta value can be something easy like 0.

    return toCart(r_sum, cyl_coord[1], z_sum)

def EfieldX(p:np.ndarray):
    """
    Controller for what E method is used.

    Inputs:
    p: the target coordinate.
    """
    global E_Method, E_Args
    #print(f"E_method is: {E_Method}")
    match E_Method:
        case "Zero":
            return np.zeros(3)
        case "Fw":
            E = np.apply_along_axis(Fw, 0, p)
        case "Bob_e":
            E = Bob_e(p)
            #print(f"Bob_e says E is: {E}")
            
            return np.array(E)


# boris push calculation
# this is used to move the particle in a way that simulates movement from a magnetic field
def borisPush(executor=None, output=None):
    """
    INTERNAL VARS
    Gyroradius:
        gyro_time: the time in sec it takes for one gyration.
            > as of now, this was calculated using the gyroradius formula assuming B = 1T, and the particle is a proton.
    """
    global df, num_parts, num_points, dt, sim_time, B_Method, E_Method, E_Args,c # Should be fine in multiprocessing because these values are only read,,,
    global manager_queue
    #print(df)
    temp = 100000  # replace later with flush_count param after adding it to the tempfile

    ## Collect coil location to know when the particle escapes
    side = c[0].position
    side = np.absolute(max(side.min(), side.max(), key=abs))

    ## Mass and Charge are hard coded to be protons right now
    mass = proton.mass # kg
    charge = proton.q #coulumb

    vAc = 1

    ## Time trackers
    ft = 0 # tracker for total simulation time
    comp_start = t.time() # tracker for computational time

    # Step 1: Create the AoS the process will work with
    #     > These conditions are read from inp file, currently stored in df.

    out = np.empty(shape = (temp + 1), dtype=particle) # Empty np.ndarray with enough room for all the simulation data, and initial conditions.

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
                            ex = 0,
                            ey = 0,
                            ez = 0,
                            id = id,
                            step = 0)

    # Step 2: do the actual boris logic
    for time in range(1, num_points + 1): # time: step number
        x = np.array([out[time - 1].px, out[time - 1].py, out[time - 1].pz])
        v = np.array([out[time - 1].vx, out[time - 1].vy, out[time - 1].vz])
        ##########################################################################
        # COLLECT FIELDS
            # submit the field calculations to the threadpool
        _Ef = executor.submit(EfieldX, x)
        _Bf = executor.submit(Bfield, x)
            # collect the results
        Ef = _Ef.result()
        Bf = _Bf.result()
            # update array entry with results
        out[time - 1].bx, out[time - 1].by,out[time - 1].bz = Bf # update B field for particle we just found
        out[time - 1].ex, out[time - 1].ey,out[time - 1].ez = Ef # update E field for particle we just found

        ##########################################################################
        # BORIS LOGIC
            # define and run all the independently obtainable values w/ threads.
        def _tt_and_ss_get():
            tt = charge / mass * Bf * 0.5 * dt
            ss = 2. * tt / (1. + tt * tt)
            return tt, ss
        def _v_minus_get():
            return v + charge / (mass * vAc) * Ef * 0.5 * dt
            # submit to executor
        _tt, _ss = executor.submit(_tt_and_ss_get)
        _v_minus = executor.submit(_v_minus_get)
            # get values from future
        tt = _tt.result()
        ss = _ss.result()
        v_minus = _v_minus.result()

            # The rest are entangled enough to rule out multithreading.
        v_prime = v_minus + np.cross(v_minus, tt)
        v_plus = v_minus + np.cross(v_prime, ss)
        v = v_plus + charge / (mass) * Ef * 0.5 * dt

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
                            ex = 0,
                            ey = 0,
                            ez = 0,
                            id = id,
                            step = time)

        ft += dt # total time spent simulating
        
        #TIME STEP SCALING
        ##check ion gyrofrequency
        """
        we are aiming for 100 steps per gyration, so we find the
        so we find the time it takes for 1 gyration at the particle's B and divide it by 100
        """
        #Bmag = np.linalg.norm(Bf)
        #curr_gyrofreq = (charge * Bmag)/mass #rads/sec
        #curr_time = 2 * np.pi / curr_gyrofreq
    
        #dt = curr_time/100
        if fromTemp['dt_bob'] == 1 and time % 50 == 0:
            _dt = dt
            dt = bob_dt_step(Bp=Bf, B0_mag=fromTemp['bob_dt_B0']['B_mag'], dt0=fromTemp['bob_dt_dt0'], min=fromTemp['bob_dt_min'], max=fromTemp["bob_dt_max"])
            print(f"dt changed to: {dt} from: {_dt}")
        if time % 1000 == 0:
            manager_queue.put(time)
            print(f"boris calc * {time} for particle {id}")
            print("total time: ", ft, dt, Ef, Bf)
        """
        Periodically add contents to the appropriate datasets in the h5 outputs file.
        """
        if time % temp == 0:
                # convert the data array of structures to pd.DataFrame
            df = pd.DataFrame([p.__dict__ for p in out])

                # append to position dataset
            df_pos = df[['px', 'py', 'pz']]
            df_pos.to_hdf(f"{output}/src/position", mode='a', append=True, index=False)
                # append to velocity dataset
            df_vel = df[['vx', 'vy', 'vz', 'vperp', 'vpar', 'vmag']]
            df_vel.to_hdf(f"{output}/src/velocity", mode='a', append=True, index=False)
                # append to field datasets
            df_fields_b = df[['bx', 'by', 'bz']]
            df_fields_b.to_hdf(f"{output}/src/fields/b", mode='a', append=True, index=False)
            df_fields_e = df[['ex', 'ey', 'ez']]
            df_fields_e.to_hdf(f"{output}/src/fields/e", mode='a', append=True, index=False)

            out = np.empty(shape=(temp + 1), dtype=particle)  # reset the internal AoS

        if np.absolute(max(x.min(), x.max(), key=abs)) > side:
                out = out[out != np.array(None)]
                print('Exited Boris Push Early')
                break
    
    comp_time = t.time() - comp_start
    diags = {
        "Particle id" : id,
        "Computation Time" : comp_time,
        "Simulation Time" : ft
    }
    return out, diags


from multiprocessing import Manager
fromTemp = None

def create_shared_info():
    manager = Manager()
    shared = manager.dict()

    shared.update(read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1]))
    return shared

def init_process(data, n1, n2, t, t1, Bf, Ef, coils, _fromTemp, queue):
    global df, num_parts, num_points, dt, sim_time, B_Method, E_Method, E_Args, c, c_cnr, fromTemp
    global fromTemp, manager_queue
    
    fromTemp = _fromTemp
    manager_queue = queue
    
    df = data
    num_parts = n1
    num_points = n2
    dt = t
    sim_time = t1
    #sources = GetCurrentTrace(c, dia, res=100, nsteps=100)

    B_Method = Bf

    E_Method = list(Ef.keys())[0]
    E_Args = Ef[E_Method]

    # Magpy collection object with all the coils
    c = coils

    ## List of all the coil center coordinates.
    ## Used in some E field implementations.
    c_centers = np.array([s.position for s in c.children_all])
    ## List of all the coil radii.
    c_radii = np.array([s.diameter for s in c.children_all])
    c_cnr = np.column_stack((c_centers, c_radii))


    #print("data shared: ", data, n1, n2, t)
"""
Will eventually replace runsim(), development grounds for a new structure.    
"""
def _runsim(manager_queue):
    _fromTemp = create_shared_info()
    with ThreadPoolExecutor() as executor:
        borisPush(executor, _fromTemp['output_file'])


def runsim(fromGui:dict, manager_queue):
    #print('simulation starting')
    _fromTemp = create_shared_info()
    dfIn = pd.DataFrame(_fromTemp['Particle_Df'])
    numPa = dfIn.shape[0]
    numPo = int(_fromTemp['numsteps'])
    tScale = _fromTemp['dt']
    time = numPo * tScale
    Bf = _fromTemp["Field_Methods"]["B"]
    Ef = _fromTemp["Field_Methods"]["E"]
    coils = _fromTemp['coils']
    coilName = _fromTemp['coil_file_name']

    init_process(dfIn, numPa, numPo, tScale, time, Bf, Ef, coils, _fromTemp, manager_queue)
    values = range(numPa)
    with ProcessPoolExecutor(initializer=init_process, initargs=(dfIn, numPa, numPo, tScale, time, Bf, Ef, coils, _fromTemp, manager_queue)) as executor:
        futures = executor.map(borisPush, values)

    out = []
    diags = []
    for future, diag in futures:
        out.append(future)
        diags.append(diag)

    ## Turn the list of dictionaries into a dataframe for ease of output.
    diags = pd.DataFrame(diags)
    ## Turn list of output data into an array for ease of access
    out = np.asarray(out)

    dir = CreateOutput(out, sim_time, num_points, num_parts, dfIn, Bf, Ef, coilName, diags)
    #graph_trajectory(lim=side, data=dir)

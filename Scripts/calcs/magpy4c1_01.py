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
from files.PusherClasses import particle, position_dt, velocity_dt, field_e_dt, field_b_dt
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

#from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict
#from system.temp_file_names import m1f1, param_keys

from settings.configs.funcs.config_reader import runtime_configs
from calcs.magpy4c1_manager_queue_datatype import Manager_Data

from EFieldFJW.efieldring_4 import fwysr_e
from EFieldFJW.streamlines3Dring import compute_field
from scipy.interpolate import RegularGridInterpolator

from system.state_dict_main import AppConfig
from EFieldFJW.e_solvers import *

import logging
from logs.setup import setup_logger

# please dont truncate anything
pd.set_option('display.max_columns', None)

####################
# PHYSICS SETTINGS #
####################
#=========#
# B FIELD #
#=========#
is_logging_e = False
# unless it is outside of the bounds given by 'side'
def Bfield(y, method, c, interp):
    if interp is None:
        if(method == "zero"):
            return np.zeros(3)

        Bf = c.getB(y, squeeze=True)
        return np.array(Bf)
    else:
        # interpolator should be called for this point
        print(f"USING INTERPOLATOR FOR B")
        return interp([y]).squeeze()

# global variables
magpy.graphics.style.CurrentStyle(arrow=None)
accel = None
dax = None
#=========#
# E FIELD #
#=========#
"""
Extra wrapper functions to gather inputs to plug into the implementation.
"""
def Fw(coord:float, fromTemp):
    """
    Fw analytic E field equation
    """
    E_Args = fromTemp["field_methods"]['e']['params']
    A = float(E_Args["A"])
    Bx = float(E_Args["B"])
    #print(f"coord: {coord}, A: {A}, B: {Bx}")
    return np.multiply(A * np.exp(-(coord / Bx)** 4), (coord/Bx)**15)


def _Bob_e(inCoord, c, res):
    """
    The internal function passed to each thread in Bob_e().

    Inputs:
    inCord: the coordinate of the point to calculate E at.
    cnr: the coordinate of the circle's center and its radius.
    """

    q = c.current # charge
    #print(f"running with the q:{q}")
    
    # To make the target point relative to the coil, we call the bob_e.impl's alignment func.
    normCoord = bob_e_impl.OrientPoint(c=c, point=inCoord)
    radius = c.diameter / 2
    normCoord = toCyl(normCoord)
    # Then pass this as the coordinate parameter of the implementation.
    z, r = bob_e_impl.at(coord = normCoord, q=q, resolution=int(res), radius= radius, convert=False)
    cart = toCart(r, normCoord[1], z)
        # since we most likely rotated the point by the inverse rotation of the coil,
        # we need to also forward rotate the results to get the E field oriented correctly.
    cart = c.orientation.apply(cart)
    return cart

def __Bob_e(coord, args):
    """
    This function will utlize multithreading, with each coil
    calculating its own e-field on a new thread.
    """
    es = [] # collection of cartesian E field components for each coil
    E_collection = args['collection']
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_Bob_e, coord, coil, args): coil for coil in E_collection}

        # Gather the data from futures once completed.
        for index, task in enumerate(futures):
            result = task.result() # cartesian form of E field
            es.append(result)
    return np.sum(es, axis=0) # sum the E field components column-wise

def Bob_e(coord, res, collection):
    """
    This function will utlize multithreading, with each coil
    calculating its own e-field on a new thread.
    """
    es = [] # collection of cartesian E field components for each coil
    for coil in collection:
        cart = _Bob_e(coord, coil, res)
        es.append(cart)

    return np.sum(es, axis=0) # sum the E field components column-wise

from EFieldFJW.ys_3d_disk import compute_disk_with_collection, compute_fields
#from EFieldFJW.washerPhiVectorized import compute_field as compute_washerPhi
from EFieldFJW.washersPhi_vectorized import washer_phi_from_collection

def EfieldX(p:np.ndarray, fromTemp, executor, interpolator, e_args):
    """
    Controller for what E method is used.

    Inputs:
    p: the target coordinate.
    """
    global dax, is_logging_e
    if interpolator is not None:
        if fromTemp.e.logging == 1 and is_logging_e:
            # check if interpolator is made
            logging.debug(f"Interpolated value: {interpolator([p])}")
        return interpolator([p]).squeeze()

    E_Method = fromTemp.e.method
    #print(f"E_method is: {E_Method}")
    match E_Method:
        case "zero":
            E =  np.zeros(3)
        case "fw":
            E = np.apply_along_axis(Fw, 0, p, fromTemp)
        case "bob_e":
            E = Bob_e(p, fromTemp.e.res, fromTemp.e.collection)
            np.empty(0).sum()  # force numpy thread finish
            #print(f"Bob_e says E is: {E}")
        case "fw_e":
            # call the appropriate function to get the value
            E = compute_field(p, fromTemp.e.collection, int(fromTemp.e.res), executor)
            np.empty(0).sum()  # force numpy thread finish
        case 'disk_e':
            inners = fromTemp.e.inner_r
            E = compute_disk_with_collection(p, fromTemp.e.collection, inners, executor)

            
    return np.array(E)

import os
import h5py
def write_to_hdf5(from_temp, out, expand_length, num_points):
        # notify terminal
    print(f"Flushing to h5 file")

        # take away all None type entries
    #print(out.shape)
    _out = out[out != np.array(None)]
    _out = _out[1:]
    #print(_out)
    df = pd.DataFrame([p.__dict__ for p in _out])
    #print(df)
    path = os.path.join(str(runtime_configs['Paths']['outputs']), from_temp.path.hdf5)
    #print(path)

    # append to position dataset
    df_pos = np.ascontiguousarray(df[['px', 'py', 'pz']].astype(dtype=np.float64).to_numpy()).view(dtype=position_dt).reshape(-1)
    #print(df_pos)
    #df_pos.to_hdf(path, key='src/position', mode='a', append=True)
    # append to velocity dataset
    df_vel = np.ascontiguousarray(df[['vx', 'vy', 'vz', 'vperp', 'vpar', 'vmag']].astype(np.float64).to_numpy()).view(dtype=velocity_dt).reshape(-1)
    #df_vel.to_hdf(path, key='src/velocity', mode='a', append=True)
    # append to field datasets
    df_fields_b = np.ascontiguousarray(df[['bx', 'by', 'bz', 'bmag', 'bhx', 'bhy', 'bhz']].astype(np.float64).to_numpy()).view(dtype=field_b_dt).reshape(-1)
    #df_fields_b.to_hdf(path, key='src/fields/b', mode='a', append=True)
    df_fields_e = np.ascontiguousarray(df[['ex', 'ey', 'ez', 'eperp', 'epar', 'emag']].astype(np.float64).to_numpy()).view(dtype=field_e_dt).reshape(-1)
    #df_fields_e.to_hdf(path, key='src/fields/e', mode='a', append=True)

    with h5py.File(path, 'a') as f:
        old_shape = f['/src/position'].shape[0]
        if old_shape < num_points + 1:
            f['/src/position'].resize((old_shape + len(df)), axis=0)
            f['/src/position'][old_shape:] = df_pos

            old_shape = f['/src/velocity'].shape[0]
            f['src/velocity'].resize((old_shape + len(df)), axis=0)
            f['/src/velocity'][old_shape:] = df_vel

            old_shape = f['src/fields/b'].shape[0]
            f['src/fields/b'].resize((old_shape + len(df)), axis=0)
            f['src/fields/e'].resize((old_shape + len(df)), axis=0)
            f['src/fields/b'][old_shape:] = df_fields_b
            f['src/fields/e'][old_shape:] = df_fields_e
    
        # reset the internal container array
    last_struct = _out[-1] # indexing _out so this is guaranteed to not be None for whatever reason.
    out = np.empty(out.shape, dtype=particle)
    out[0] = last_struct

    return out


# boris push calculation
# this is used to move the particle in a way that simulates movement from a magnetic field
def borisPush(executor=None, from_temp=None, manager_queue=None, b_interp = None, e_interp = None):
    """
    INTERNAL VARS
    Gyroradius:
        gyro_time: the time in sec it takes for one gyration.
            > as of now, this was calculated using the gyroradius formula assuming B = 1T, and the particle is a proton.
    """
    #global df, num_parts, num_points, dt, sim_time, B_Method, E_Method, E_Args,c # Should be fine in multiprocessing because these values are only read,,,
    #print(df)
    temp = 100000  # replace later with flush_count param after adding it to the tempfile

    # determine constants for field calculations
    e_args = {} # extra arguments supplied to E calculation
    def calc_e_consts():
        method = from_temp.e.method
        match method:
            case 'washer_potential':
                e_c:magpy.Collection
                e_c = from_temp.e.collection
                # assemble extra function arguments for the solution
                #   Generally will be in lists with the same indexing order as the collection

                normals = [] # input n_coils amount of (3,) arrays
                sigmas = [] # input n_coils amount of empty lists
                for ring in e_c.children_all:
                    # we can get the coil's normal by rotating [0, 0, 1] by the coil's orientation.
                    default_z = np.array([0,0,1])
                    normals.append(ring.orientation.apply(default_z))

                    # append empty list per coil into sigmas
                    sigmas.append([])

                # put all argument extras inside the e_args dict
                e_args['normals'] = normals
                e_args['sigmas'] = sigmas

        return e_args

    calc_e_consts()

    ## Collect coil location to know when the particle escapes
    mag_c = from_temp.b.collection
    dt = from_temp.step.dt
    if from_temp.b.method == 'zero':
        side = 5
    else:
        _side = mag_c[0].position
        side = np.absolute(max(_side.min(), _side.max(), key=abs))

    ## Mass and Charge are hard coded to be protons right now
    mass = proton.mass # kg
    charge = proton.q #coulumb

    vAc = 1

    ## Time trackers
    ft = 0 # tracker for total simulation time
    comp_start = t.time() # tracker for computational time

    # Step 1: Create the AoS the process will work with
    #     > These conditions are read from inp file, currently stored in df.
    expand_length = (temp * from_temp.particle.count)
    out = np.empty(((temp * from_temp.particle.count) + 1), dtype=particle) # Empty np.ndarray with enough room for all the simulation data, and initial conditions.

    #temp = df["starting_pos"].to_numpy()[id] # Populate it with the initial conditions at index 0.
    #temp1 = df["starting_vel"].to_numpy()[id] * 6
    #df = from_temp['Particle_Df']
    df = pd.read_csv(from_temp.path.particle, dtype=np.float64)
    row = df.iloc[0]
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
    num_points = int(from_temp.step.numsteps)
    print(f"setup complete, beginning steps")
    i = 1
    for time in range(1, num_points + 1): # time: step number
        #print(f"step {i}")
        x = np.array([out[i - 1].px, out[i - 1].py, out[i - 1].pz])
        v = np.array([out[i - 1].vx, out[i - 1].vy, out[i - 1].vz])
        ##########################################################################
        # COLLECT FIELDS
            # submit the field calculations to the threadpool
        _Ef = executor.submit(EfieldX, x, from_temp, executor, e_interp, e_args)
        _Bf = executor.submit(Bfield, x, from_temp.b.method, mag_c, b_interp)
            # collect the results
        Ef = _Ef.result()
        #print(Ef)
        Bf = _Bf.result()
            # update array entry with results
        out[i - 1].bx, out[i - 1].by,out[i - 1].bz = Bf # update B field for particle we just found
        out[i - 1].ex, out[i - 1].ey,out[i - 1].ez = Ef # update E field for particle we just found

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
        _tt_ss = executor.submit(_tt_and_ss_get)
        _v_minus = executor.submit(_v_minus_get)
            # get values from future
        tt, ss = _tt_ss.result()
        v_minus = _v_minus.result()

            # The rest are entangled enough to rule out multithreading.
        v_prime = v_minus + np.cross(v_minus, tt)
        v_plus = v_minus + np.cross(v_prime, ss)
        v = v_plus + charge / (mass) * Ef * 0.5 * dt

        # Update particle information with the pos and vel
        position = x + v * dt 
        # velocity = v_plus + charge / (mass * vAc) * E * 0.5 * dt
        out[i] = particle(px = position[0],
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
        if from_temp.step.dynamic.on:
            _dt = dt
            dt = bob_dt_step(Bp=Bf,
                             B0_mag=from_temp.step.dynamic.consts.B0.b_norm,
                             dt0=from_temp.step.dynamic.consts.dt0,
                             min=from_temp.step.dynamic.consts.dt_min,
                             max=from_temp.step.dynamic.consts.dt_max)
            print(f"dt changed to: {dt} from: {_dt}")

        if time % 1000 == 0:
            manager_queue.put(Manager_Data(step=time, do_stop=False))
            print(f"boris calc * {time} for particle {id}")
            print("total time: ", ft, dt, Ef, Bf)
        """
        Periodically add contents to the appropriate datasets in the h5 outputs file.
        """
        if time % temp == 0:
            x = np.array([out[i].px, out[i].py, out[i].pz])
            v = np.array([out[i].vx, out[i].vy, out[i].vz])
            ##########################################################################
            # COLLECT FIELDS
            # submit the field calculations to the threadpool
            _Ef = executor.submit(EfieldX, x, from_temp, executor, e_interp,
                                  e_args)
            _Bf = executor.submit(Bfield, x, from_temp.b.method, mag_c, b_interp)
            # collect the results
            Ef = _Ef.result()
            Bf = _Bf.result()

            # update array entry with results
            out[i].bx, out[i].by, out[i].bz = Bf  # update B field for particle we just found
            out[i].ex, out[i].ey, out[i].ez = Ef  # update E field for particle we just found
            _out = write_to_hdf5(from_temp, out, temp, num_points)
            #out[0] = out[time]
            #out[1:] = None
            i = 0  # reset the internal AoS index
            out = _out
            #print(out)

        if np.absolute(max(x.min(), x.max(), key=abs)) > side:
                out = out[out != np.array(None)]
                print('Exited Boris Push Early')
                break
        i += 1
    comp_time = t.time() - comp_start
    diags = {
        "Particle id" : id,
        "Computation Time" : comp_time,
        "Simulation Time" : ft
    }
    if(i != 1):
        write_to_hdf5(from_temp, out, expand_length, num_points)
    #print(f"finished writing to file")
    manager_queue.put(Manager_Data(step=num_points, do_stop=True))


from multiprocessing import Manager
fromTemp = None

def create_shared_info():
    """
    deprecated, as the shared info comes directly from the app by reference.
    """
    manager = Manager()
    shared = manager.dict()

    #shared.update(read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1]))
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
from grid._3d_mesh import precalculate_3d_grid
from EFieldFJW.ys_3d_disk import fields_from_grid
from pathlib import Path
from RETerry import bob_e

def create_interpolator(filepath):
    with h5py.File(filepath, 'r') as f:
        # get the linspace used in the grid
        ax_linspace = f['src/coords'][0,:,0,0] # linspace used for x; should be same for all axes
        mesh_field = f['src/data']
        mesh_field = np.moveaxis(mesh_field, 0, -1)
    interpolator = RegularGridInterpolator((ax_linspace, ax_linspace, ax_linspace), mesh_field, method='linear')
    return interpolator

def grid_checker(fromTemp, filepath):
    """
    IF the simulation is called with gridding = 1 for a ring configuration, you need to make sure
    that a grid lookup file exists.
    """
    global is_logging_e
    # check b field
    b_interpolator = None
    e_interpolator = None
    try:
        if fromTemp.b.gridding == 1 and fromTemp.b.method == "magpy":
            collection = fromTemp.b.collection
            method = collection.getB
            precalculate_3d_grid(method, Path(fromTemp.path.b))

            coil_path = Path(fromTemp.path.b)
            # stuff with the interpolator
            hdf5_name = coil_path.parents[0] / "grid" / f"{coil_path.name}.hdf5"
            b_interpolator = create_interpolator(hdf5_name)
    except KeyError:
        pass

    # check e field
    # TODO: extend functionality with e methods <3
    try:
        if fromTemp.e.gridding == 1 and fromTemp.e.method == 'disk_e':
            print('creating e grid')
            method = fields_from_grid
            collection = fromTemp.e.collection
            inners = fromTemp.e.inner_r
            args = {
                'c' : collection,
                'inners' : inners
            }
            coil_path = Path(fromTemp.path.e)
            precalculate_3d_grid(method, coil_path, **args)

            hdf5_name = coil_path.parents[0] / "grid" / f"{coil_path.name}.hdf5"
            e_interpolator = create_interpolator(hdf5_name)

        if fromTemp.e.gridding == 1 and fromTemp.e.method == 'bob_e':
            method = bob_e.bob_e_from_collection
            collection = fromTemp.e.collection
            coil_path = Path(fromTemp.path.e)
            precalculate_3d_grid(method, Path(fromTemp.path.e), collection=collection)

            hdf5_name = coil_path.parents[0] / "grid" / f"{coil_path.name}.hdf5"
            e_interpolator = create_interpolator(hdf5_name)

        if fromTemp.e.method == 'washer_potential':
            # precompute the grid potential
            print(f"creating washer potential")
            e_c = fromTemp.e.collection
            #b = e_c[0].diameter / 2
            a = float(fromTemp.e.inner_r[0])
            #Q = e_c[0].current
            res = 101 # hardcoded for now

            sim_lim = np.max(abs(e_c[0].position)) + 0.005
            _lin = np.linspace(-sim_lim, sim_lim, res)
            dax = _lin[1] - _lin[0]
            _x, _y, _z = np.meshgrid(_lin, _lin, _lin, indexing='ij')
            points = np.stack([_x.ravel(), _y.ravel(), _z.ravel()], axis=-1)

            # collect coil information
            normals = []  # input n_coils amount of (3,) arrays
            sigmas = []  # input n_coils amount of empty lists
            for ring in e_c.children_all:
                # we can get the coil's normal by rotating [0, 0, 1] by the coil's orientation.
                default_z = np.array([0, 0, 1])
                normals.append(ring.orientation.apply(default_z))

                # append empty list per coil into sigmas
                sigmas.append([])

            # LOG STUFF IF CALLED TO DO SO.
            #print(fromTemp.e.logging)
            if fromTemp.e.logging == 1:
                is_logging_e = True
                print(f"logging file should be made")
                setup_logger("e.log")

                logging.info(f"Field_Method: Washer_Potential")
                logging.info(f"Collection has {e_c.children_all} coils")
                logging.info(f"Working with q: {e_c[0].current}, a: {a}")
                logging.info(f"sim_lim is: {sim_lim}")

            potential = washer_phi_from_collection(points, e_c, a, normals, sigmas)
            potential = potential.reshape((res, res, res))

            # save the gradient to the global var.
            dphi_dx, dphi_dy, dphi_dz = np.gradient(potential, dax, dax, dax)
            Ex = -dphi_dx
            Ey = -dphi_dy
            Ez = -dphi_dz

            E_grid = np.stack([Ex, Ey, Ez], axis=-1)
            e_interpolator = RegularGridInterpolator((_lin, _lin, _lin), E_grid, method='linear')
            print(f"Finished creating interpolator for washer potential derived E")

    except KeyError:
        pass
    #print(e_dict['method'])
    #print(f"finished making interpolators")
    return b_interpolator, e_interpolator

def _runsim(manager_queue, params:AppConfig):
    filepath = ""
    """
    This try/ except block exists to ensure that the tempfile created in some methods
    are properly erased when the program exits.
    """
    # Access tempfile dict for all threads
    _fromTemp = params

    # check/ create precomputed grid
    # value of these will be None if gridding not used.
    b_inter, e_inter = grid_checker(_fromTemp, filepath)

    with ThreadPoolExecutor() as executor:
        borisPush(executor, _fromTemp, manager_queue, b_inter, e_inter)


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

import numpy as np
import settings.constants as constants
from system.temp_manager import TEMPMANAGER_MANAGER, update_temp, read_temp_file_dict
from system.temp_file_names import m1f1, param_keys
from definitions import DIR_ROOT
import pickle
"""
Extra logic to run before a simulation for Bob's variable timestep.
Defines constants that need to be calculated.
(B0, f0, dt0)

Ideally, the coil configuration meets these reqs:
1. Symmetric for the B0 
2. (at least for now) z-axis coils need to exist for B0 to be realistic
because it's going to sample the z-axis.

PARAMETERS:
c (magpylib.Collection): the coil configuration
particle (ion class): the particle used in the simulation; defaults to a proton
"""
def before_simulation_bob_dt(particle=constants.proton):
    #print(TEMPMANAGER_MANAGER.files[m1f1])
    d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
    c = d[param_keys.field_methods.name]['b']['params']['collection']
    ref_p = float(d[param_keys.dt_bob_prop.name])
    dyn_rng = float(d[param_keys.dt_bob_dyn_rng.name])
    # GET THE POSITION FOR B0
    # since we are assuming that the first coil is displaced only on one axis and that the configuration is 
    # symmetric, I index the first child and find its maximum to know how much the coils are displaced.
    offset = c[0].position[np.argmax(abs(c[0].position))]
    _ax = np.argmax(abs(c[0].position))

    B0_pos = np.zeros(3)
    B0_pos[_ax] = offset * ref_p
    
    # GET INFORMATION FROM B0 POSITION
    B0_B = c.getB(B0_pos)
    B0_B_norm = np.linalg.norm(B0_B)
    #print(f"funcs.before_simulation_bob_dt; B0_B_norm: {B0_B_norm}")

    # GET f0
    f0 = 1.52e7 * particle.anum * B0_B_norm
    #print(f0)

    # GET dt0
    dt0 = 1/f0

    d = {
        "bob_dt_B0": {"position" : B0_pos,
                  "B" : B0_B,
                  "B_mag" : B0_B_norm},
        "bob_dt_f0" : f0,
        "bob_dt_dt0" : dt0,
        "bob_dt_min" : dt0 / dyn_rng,
        "bob_dt_max" : dt0 * dyn_rng
                  }

    update_temp(TEMPMANAGER_MANAGER.files[m1f1], 
                d)
    return d
import shutil
import os
from settings.configs.funcs.config_reader import runtime_configs
def copy_diags_to_output_subdir():
    d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
    #out_path = os.path.join(str(runtime_configs['Paths']['outputs']), d["output_path"])
    out_path = d[param_keys.output_path.name]
    coil_path = d['coil_file']
    particle_path = d['particle_file']

        # update the tempfile with the used path names.
    d[param_keys.hdf5_path.name] = os.path.join(out_path, 'data.hdf5')
    d[param_keys.output_path.name] = out_path
    update_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

    # TODO: ADD BOB_E FILE IF USED
        # check whether the current tempfile has the bob_e rings configured to be used.
    if d[param_keys.field_methods.name]['e']['method'] == "Bob_e":
        # if the method is used, then copy the configured coil file and binary to the input folder
            # create an empty file for the csv
            with open(os.path.join(out_path, 'e_rings.txt'), 'w') as f:
                pass
            # copy the configured bob_e coil f
            shutil.copyfile(src=d['bob_e_file'], dst=os.path.join(out_path, 'e_rings.txt'))


        # copy the used coil file to the output
    with open(os.path.join(out_path, "coils.txt"), 'w') as f:
        pass
    with open(os.path.join(out_path, "particles.txt"), 'w') as f:
        pass

    shutil.copyfile(coil_path, os.path.join(out_path, "coils.txt"))
    shutil.copyfile(particle_path, os.path.join(out_path, "particles.txt"))


"""
Function to direct all widgets to extract relevant data from the last_used file (if it exists)
then update the current runtime tempfile dictionary with it.

Updates the tempfile with default values at the hint of a failure (implemented at each widget definition)
"""
def initialize_tempfile_dict(widgets:list):
        # first step: read the last_used file dictionary, which is placed in the project root
    if not os.path.exists(os.path.join(DIR_ROOT, 'last_used')):
        lu = None
    else:
        lu = read_temp_file_dict(os.path.join(DIR_ROOT, 'last_used'))
        #print(lu)
    for widget in widgets:
        widget.init_temp(lu)
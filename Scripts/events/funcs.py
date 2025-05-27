import numpy as np
import settings.constants as constants
from system.temp_manager import TEMPMANAGER_MANAGER, update_temp, read_temp_file_dict
from system.temp_file_names import m1f1
from definitions import DIR_ROOT
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
def before_simulation_bob_dt(particle=constants.proton, drange=10):
    #print(TEMPMANAGER_MANAGER.files[m1f1])
    c = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])['coils']
    
    # GET THE POSITION FOR B0
    # since we are assuming that the first coil is displaced only on one axis and that the configuration is 
    # symmetric, I index the first child and find its maximum to know how much the coils are displaced.
    offset = c[0].position[np.argmax(c[0].position)]
    B0_pos = [0, 0, offset/2]
    
    # GET INFORMATION FROM B0 POSITION
    B0_B = c.getB(B0_pos)
    B0_B_norm = np.linalg.norm(B0_B)

    # GET f0
    f0 = 1.52e7 * particle.anum * B0_B_norm

    # GET dt0
    dt0 = 1/f0

    update_temp(TEMPMANAGER_MANAGER.files[m1f1], 
                {
        "bob_dt_B0": {"position" : B0_pos,
                  "B" : B0_B,
                  "B_mag" : B0_B_norm},
        "bob_dt_f0" : f0,
        "bob_dt_dt0" : dt0,
        "bob_dt_min" : dt0 / drange,
        "bob_dt_max" : dt0 * drange
                  })
import shutil
import os
from settings.configs.funcs.config_reader import runtime_configs
def copy_diags_to_output_subdir():
    d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
    out_path = os.path.join(str(runtime_configs['Paths']['outputs']), d["output_path"])
    coil_path = d['coil_file']
    particle_path = d['particle_file']

    # TODO: ADD BOB_E FILE IF USED

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
    lu = read_temp_file_dict(os.path.join(DIR_ROOT, 'last_used'))
    for widget in widgets:
        widget.init_tempfile(lu)
import numpy as np

"""
Implementation of Bob's variable time step

# PARAMETERS
Bp, Ep (arrays) : container with shape of 3, represents the B (in T) and E (V/m) at the target point
B0 (array) : container with shape of 3, represents the B (in T) at the midpoint along coil axis segment from coil center and origin.
drange (int, default = 10) : controls the factor of the timestep's range of allowable values
"""
# As you will see, ion info is hard coded to be protons right now.
# It is hella expandable though if you want to add more ions.
def bob_dt_step(Bp, B0_mag, dt0, min, max):
    Bp_mag = np.linalg.norm(Bp)

    # get dtp
    dtp = (B0_mag / Bp_mag) * dt0

    # check dtp
    dtp = np.max(((min), np.min((dtp, max))))

    return dtp
'''
Holds functions for calculating loss, moment, etc.
'''

import numpy as np

def CalculateLoss(vels:np.ndarray, bs:np.ndarray, intervals:int):
    '''
    Selects given or default intervals from the data, then returns the mag. moment for each.

    Equation used from: https://farside.ph.utexas.edu/teaching/plasma/lectures/node18.html
        - (2.48) for the magnetic moment
            > mu = (mass * vcross^2)/(2B)
    
    PARAMETERS
    vels: an array of all the particle velocity components
    bs: an array of all the b field components
    intervals: an int representing the number of desired points for checking the mag. moment.
        - advised to be a factor of nsteps, otherwise the floor division will approximate the correct interval.
    '''
    # TEMP TEMP TEMP TEMP
    mass = 1.672e-27 # mass is hard coded to be a proton for now. 
    
    # Data prepping
    ## Get the stride to calculate mag. moment for
    nsteps = vels.shape[0]
    stride = nsteps//intervals
    ## Filter the input arrays based on the stride.
    vels = vels[::stride]
    bs = bs[::stride]
    
    # Calculation
    ## Numerator: (m * vcross^2)
    vcross = np.cross(vels, bs)
    vcross_sq = np.array(list((map(lambda x: np.dot(x,x), vcross))), dtype=float)
    #print(vcross_sq)
    mass_x_cross = vcross_sq * mass
    ## Denominator: 2B
    b_mag_mult = 2 * np.sqrt(np.array(list(map(lambda x:np.dot(x,x), bs)), dtype=float))
    ### Check if any of the denominator is 0, then remove them from both arrays
    b_mag_zeros = np.where(b_mag_mult == 0)

    for ind in b_mag_zeros:
        np.delete(mass_x_cross, ind)
        np.delete(b_mag_mult, ind)

    return np.divide(mass_x_cross, b_mag_mult)

def _ArrCentralDiff(arr:np.ndarray):
    '''
    returns an np.ndarray of the central differences
    '''
    arrplus = arr[2:]
    arrminus = arr[:-2]

    return ((arrplus - arrminus) / 2)
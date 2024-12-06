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
    #vels = vels[:-1:stride]
    #bs = bs[:-1:stride]
    
    # Calculation
    ## Numerator: (m * vcross^2)
    vcross = np.cross(vels, bs)
    vcross_sq = np.array(list((map(lambda x: np.dot(x,x), vcross))), dtype=float)

    mass_x_cross = vcross_sq * mass
    ## Denominator: 2B
    b_mag = np.sqrt(np.array(list(map(lambda x:np.dot(x,x), bs)), dtype=float))
    b_mag_mult = 2 * b_mag
    ### Check if any of the denominator is 0, then remove them from both arrays
    b_mag_zeros = np.where(b_mag_mult == 0)

    # V||
    vPar = []
    for i in range(len(vels)):
        vPar.append(np.dot(vels[i], bs[i]))
    vPar = np.array(vPar)
    
    vmag_sq = []
    for vel in vels:
        vmag_sq.append(find_energy(vel))
    #print(vPar)
    #vPar = np.power(vPar, 2)

    #vcross_mag = np.sqrt(vcross_sq)

    #v_mag = np.array(list((map(lambda x: np.dot(x,x), vels))), dtype=float)

    for ind in b_mag_zeros:
        np.delete(mass_x_cross, ind)
        np.delete(b_mag_mult, ind)

    return np.divide(mass_x_cross, b_mag_mult), b_mag, vcross_sq, vcross, vmag_sq, vels

def find_energy(array:np.array):
    
    square = np.power(array, 2)
    return np.sqrt(np.sum(square))

def _ArrCentralDiff(arr:np.ndarray):
    '''
    returns an np.ndarray of the central differences
    '''
    arrplus = arr[2:]
    arrminus = arr[:-2]

    return ((arrplus - arrminus) / 2)
'''
Holds functions for calculating loss, moment, etc.
'''

import numpy as np
import h5py

def magnitude_at_each_step(arr, f, ds_key, col_key):
    """
    takes in a 2D input array and returns a 1D array containing the magnitudes at axis 1.
    in: [[x1,y1,z1],[x2,y2,z2],...[xn,yn,zn]]
    out: [mag1, mag2, mag3]
    """
        # if any of the selected magnitude dataset column has a None value,
        # then it is a sign to calculate and populate it.
    #print(f[ds_key][col_key])
    if np.isnan(f[ds_key][col_key]).any():
        #print("yes")
        mag = np.linalg.norm(arr, axis=1)
        f[ds_key][col_key] = np.where(mag == 0, 1e-12, mag)
    return f[ds_key][col_key]

    #return np.linalg.norm(arr, axis=1)

def get_parallel(bs, arr, f, ds_key, col_key):
    """
    Returns the parallel decomposition of the arr 'arr' that is travelling in the 'bs' direction.

    out = (arr dot bs / mag(bs)) * bs
    """
    #print(f"parallel called")
        # since all the reasons this function will be called will involve the magnitude of b,
        # I can hard code its reference in the h5 file.
    if np.isnan(f['src/fields/b']['bmag']).any():
        f['src/fields/b']['bmag'] = magnitude_at_each_step(bs, f, 'src/fields/b', 'bmag')

    #print(f"bmag finished")
    if np.isnan(f['src/fields/b']['bhx']).any():
        #print(f"calculating bhat")
        mag = f['src/fields/b']['bmag']
        f['src/fields/b']['bmag'] = np.where(mag == 0, 1e-12, mag)
        #print(bs.shape, mag.shape)
        #print(bs / np.array(mag)[:, np.newaxis])
        bhat = bs / np.array(mag)[:, np.newaxis]
        #print(bhat)
        bhx, bhy, bhz = np.split(bhat,3, axis=1)
        #print(bhy)
        #print(bhz)
        # (n, 3) / (n, )
        # (n, )

        f['src/fields/b']['bhx'] = bhx.reshape(bhx.shape[0],)
        f['src/fields/b']['bhy'] = bhy.reshape(bhy.shape[0],)
        f['src/fields/b']['bhz'] = bhz.reshape(bhz.shape[0],)
    #print(f"bhat finished")
        # if any of the selected magnitude dataset column has a None value,
        # then it is a sign to calculate and populate it.
    if np.isnan(f[ds_key][col_key]).any():
        bhat = np.stack((f['src/fields/b']['bhx'], f['src/fields/b']['bhy'], f['src/fields/b']['bhz']), axis=1)
        #print(bhat.shape, arr.shape)
        dot = np.einsum('ij,ij->i',bhat,arr)
        #print(dot.shape)
        f[ds_key][col_key] = dot.reshape(dot.shape[0],)
    #print(f"Parallel is: {f[ds_key][col_key]}")
    return f[ds_key][col_key]


def get_perpendicular(bs, arr, f, ds_key, col_key):
    """
    returns the cross product's magnitude of the two arrays.
    """
    # since all the reasons this function will be called will involve the magnitude of b,
        # I can hard code its reference in the h5 file.
    if np.isnan(f['src/fields/b']['bmag']).any():
        f['src/fields/b']['bmag'] = magnitude_at_each_step(bs, f, 'src/fields/b', 'bmag')
    #print('bmag obtained')

    bhat = np.stack((f['src/fields/b']['bhx'], f['src/fields/b']['bhy'], f['src/fields/b']['bhz']), axis=1)
    #print(magnitude_at_each_step((np.cross(arr, bhat)), f, ds_key, col_key))
    return magnitude_at_each_step((np.cross(arr, bhat)), f, ds_key, col_key)

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
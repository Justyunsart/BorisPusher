'''
Holds functions for calculating loss, moment, etc.
'''

import numpy as np

def CalculateLoss(vels:np.ndarray, bs:np.ndarray):
    '''
    returns the perpendicular component between two vectors and its first, second derivatives.
    '''
    vcross = np.cross(vels, bs)
    # array of the magnitudes of the perpendicular component
    vcrossmag = np.sqrt(list(map(lambda x: np.dot(x, x), vcross))) 

    # if we get the first order derivative, we can observe the amount of time the magnitudes increase vs. decrease
    vcrossmagD1 = _ArrCentralDiff(vcrossmag)
    vcrossmagD2 = _ArrCentralDiff(vcrossmagD1)


    return vcrossmag, vcrossmagD1, vcrossmagD2

def _ArrCentralDiff(arr:np.ndarray):
    '''
    returns an np.ndarray of the central differences
    '''
    arrplus = arr[2:]
    arrminus = arr[:-2]

    return ((arrplus - arrminus) / 2)
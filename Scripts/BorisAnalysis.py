'''
Holds functions for calculating loss, moment, etc.
'''

import numpy as np

def CalculateLoss(vels:np.ndarray, bs:np.ndarray):
    vcross = np.cross(vels, bs)
    vcrossmag = list(map(lambda x: np.dot(x, x), vcross))

    return vcrossmag
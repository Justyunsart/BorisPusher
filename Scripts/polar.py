"""
Holds common functions for converting to and from polar coordinates
"""
import numpy as np
def cartesian_to_cyl(coord):
    """
    converts from a given cartesian coordinate to a polar cylindrical one.
    """
    rho = np.sqrt(coord[0] ** 2 + coord[1] ** 2)
    azimuth = np.arctan2(coord[1],coord[0])
    z = coord[2]

    return np.array([rho, azimuth, z])

def cyl_to_cartesian(coord):
    """
    converts from cylindrical to cartesian coordinates.
    """
    x = coord[0] * np.cos(coord[1])
    y = coord[0] * np.sin(coord[1])
    z = coord[2]

    return np.array([x,y,z])

'''
point = [0,1,2]
point_cyl = cartesian_to_cyl(point)
point_2 = cyl_to_cartesian(point_cyl)

print(f'point {point} in cyl is: {point_cyl}')
print(f'and back to cartesian is: {point_2}')
'''
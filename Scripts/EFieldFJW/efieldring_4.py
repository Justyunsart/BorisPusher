from Alg.circle import circle_trace
import numpy as np
from magpylib import Collection
from settings.constants import coulomb as k

"""
An alternative ring charge e-field solution.
Assumes an input of a magpylib.Collection object. This is purely because
it is handy for keeping track of position, rotation, orientations.
"""

def fwysr_e(field_coord, coils: Collection, num_points:int=200):
    # step 1
    # preallocate output array
    Es = np.empty((len(coils.children) * num_points, 3))
    dq = coils[0].current / num_points
    inps = []
    # get XY plane ring points
    def get_ring_trace(radius):
        trace = circle_trace(npoints=num_points, radius=radius)
        return trace

    for coil in coils:
        # get rx, ry, rz
        trace = get_ring_trace(coil.diameter/2)
        # orient the point
        coord = coil.orientation.apply(field_coord - coil.position, inverse=True)
        # subtraction for the inputs
        diff = coord - trace
        inps.append(diff)
    # format inps for step 2
    inps = np.array(inps).squeeze().reshape((len(coils.children) * num_points, 3))
    #print(inps)
    #-----#
    # step 2
    # get the magnitudes of each array element
    r = np.linalg.norm(inps, axis=1)
    r3 = np.where(r != 0, r ** 3, np.inf) # precaution against 0 division
    Es = k * dq * inps / r3.reshape(-1,1)
    # apply the forward rotations for each E
    for i in range(len(coils.children)):
        # index the appropriate elements of Es based on the coil index i
        start_ind = i * num_points
        end_ind = start_ind + num_points - 1
        Es[start_ind:end_ind] = coils[i].orientation.apply(Es[start_ind:end_ind], inverse=False)
    return np.sum(Es, axis=0)

if __name__ == '__main__':
    from magpylib.current import Circle
    c1 = Circle(position=np.array([0, 0, 0]), diameter=2, current=1e-11)
    #c2 = Circle(position=np.array([0, 0, 0]), diameter=2, current=1e-11)
    #c2.rotate_from_angax(90, "x")
    collection = Collection((c1))

    field_point = np.array([1, 1, 0.001])

    print(fwysr_e(field_point, collection))


import magpylib as mp
from magpylib.current import Circle
import numpy as np

import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

from dataclasses import dataclass

@dataclass
class rotation_param():
    degrees: float = 0.0
    axis: str = 'x'

def do_rotation(circle:Circle, rotations:list):
    num_steps = 100
    # perform rotations
    for rotation in rotations:
        # create the linspace for animation if you need to
        degrees = rotation.degrees
        circle.rotate_from_angax(degrees, rotation.axis)

def cartesian_to_cylindrical_th(coords):
    """
       Accepts a (res, res, 3) or (N, 3) array of vectors.
       Returns a flat array of theta angles in radians.
       """
    # Reshape to (N, 3) if needed
    coords = coords.reshape(-1, 3)

    x = coords[:, 0]
    y = coords[:, 1]

    theta = np.arctan2(y, x)  # in radians
    return theta


def graph_b_quad(c:mp.Collection, quadrant:int):
    # check inputs
    assert quadrant <= 4
    """
    with a mpl collection as an input, graph the currently selected
    magnetic coil's B field cross-section.
    """
    alpha = np.arctan(np.sqrt(2))

    # Define quadrant direction multipliers: (x_sign, z_sign)
    directions = {
        1: (1, 1, 45),
        2: (-1, 1, 135),
        3: (-1, -1, 225),
        4: (1, -1, 315)
    }
    try:
        x_sign, y_sign, angle = directions[quadrant]
    except KeyError:
        raise ValueError("Quadrant must be an integer from 1 to 4.")
    l = np.max(c[0][0].position) + c[0][0].diameter / 2 + 1

    # Set ranges based on sign
    xmin, xmax = (0, l) if x_sign > 0 else (-l, 0)
    ymin, ymax = (0, l) if y_sign > 0 else (-l, 0)
    # construct grid for the cross-section
    res = 100
    x = np.linspace(-l, l, res)
    z = np.linspace(-l, l, res)

    X, Z = np.meshgrid(x, z, indexing='xy')
    Y = np.full_like(X, 0)

    grid = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)

    #X, Y, Z = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)

    # calculate B field for the entire grid
    #Bs = np.array(c.getB(grid))  # [bx, by, bz]
    # rotate based on the quadrant
    #rot = R.from_euler('z', angle, degrees=True)
    #points = np.stack([Bs[:,0].ravel(), Bs[:,1].ravel(), Bs[:,2].ravel()], axis=1)
    #print(c.children_all)
    c.rotate_from_angax(angle, 'z', start=0)
    #Bs_rot = Bs_rot.reshape(Bs.shape)

    # Flatten Bs_rot to shape (N, 3)
    #points_flat = Bs_rot.reshape(-1, 3)

    # Create a rotation object per vector using θ from cylindrical B-field
    # Bs_th is shape (N,) in radians
    #print(Bs_th.shape)
    #rotations = R.from_euler('y', alpha)  # degrees=False by default; radian rotation time

    # Apply all rotations in batch
    c.rotate_from_angax(45, 'y', start=0)

    # Compute scalar quantity for plotting (e.g., norm of each rotated B vector)
    #Bq_flat = np.linalg.norm(rotated_vectors, axis=1)
    #print(Bq_flat.shape)

    # Reshape back to 2D grid
    #q = Bq_flat.reshape(res, res)

    Bs = np.array(c.getB(grid))  # [bx, by, bz]

    # graph
    fig, ax = plt.subplots(1, 1)
    #print(Bs.shape)
    contour = ax.contourf(X, Z, np.log(np.linalg.norm(Bs, axis=1)).reshape(100,100), levels=100)
    #contour = ax.contourf(X, Z, np.log(Bq), levels=100)
    cbar = fig.colorbar(contour)
    cbar.set_label("log(mag(B_quad.))")
    #ax.plot(Bq_flat)
    ax.grid()

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Z-axis")
    plt.show()

if __name__ == "__main__":
    from MakeCurrent import Circle as cir

    # Construct two coils from windings
    coil1 = mp.Collection(style_label="coil1")
    for z in np.linspace(-0.0005, 0.0005, 3):
        coil1.add(mp.current.Circle(current=-1, diameter=0.05, position=(0, 0, z)))
    coil1.position = (0, 0, -0.015)
    #
    coil2 = mp.Collection(style_label="coil2")
    for z in np.linspace(-0.0005, 0.0005, 3):
        coil2.add(mp.current.Circle(current=1, diameter=0.05, position=(0, 0, z)))
    coil2.position = (0, 0, 0.015)

    # SPINDLECUSP consists of two coils
    spindle = coil1 + coil2

    # DEFINE ROTATIONS
    #rotations = [rotation_param(degrees=45, axis='y'),
    #             rotation_param(degrees=45, axis='x'),]

    #c = cir(1000, 1, 1.1, 0) # hexahedron

    # perform rotations on the circle
    #do_rotation(circle, rotations)

    # add circle to collection, with hex.
    #c.add(circle)

    # after doing stuff to the independently created circle, graph b with the hex.
    graph_b_quad(spindle, 2)

    mp.show(spindle)


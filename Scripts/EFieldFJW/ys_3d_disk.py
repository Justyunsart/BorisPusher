import numpy as np
from scipy.constants import epsilon_0
from Alg.polarSpace import toCyl, toCart
from concurrent.futures import as_completed

thetas = np.linspace(0, 2 * np.pi, 200)
dtheta = thetas[1] - thetas[0]

def compute_fields(rho, z, Q, O_radius, I_radius=0, orientation=None, th=0):
    sigma = Q / (np.pi * O_radius ** 2)  # charge density C/m^2
    prefactor = sigma / (4 * np.pi * epsilon_0)

    r_vals = np.linspace(I_radius, O_radius, 200)
    dr = r_vals[1] - r_vals[0]

    # Create meshgrid of r and theta (shape: r_vals.size x thetas.size)
    R, Theta = np.meshgrid(r_vals, thetas, indexing='ij')  # R.shape = (200, 200)

    # Convert polar coordinates to Cartesian
    x = R * np.cos(Theta)
    y = R * np.sin(Theta)

    # Observation point (rho, 0, z)
    dx = rho - x           # shape (200, 200)
    dy = -y
    dz = z

    denom = (dx**2 + dy**2 + dz**2)**1.5 + 1e-20  # Avoid division by zero
    #print(denom)

    dA = R * dr * dtheta  # area element
    #print(dA)

    Erho = np.sum(dx / denom * dA)
    Ez   = np.sum(dz / denom * dA)

    E_rho = prefactor * Erho
    E_z   = prefactor * Ez

    # FORMAT OUTPUT
    # convert result back to cartesian
    E_raw = toCart(E_rho, th, E_z)
    # apply forward rotation
    E = orientation.apply(E_raw, inverse=False)

    return E

from magpylib import Collection
from concurrent.futures import ThreadPoolExecutor
from functools import partial

def _field_step_1(coord, c, inners):
    # orient point
    p_oriented = c.orientation.apply(coord - c.position, inverse=True)
    # convert coordinate to cyl
    p_cyl = toCyl(p_oriented)

    E = compute_fields(rho = p_cyl[0], z = p_cyl[2],
                   Q = c.current,
                   O_radius = c.diameter / 2,
                   I_radius = inners,
                   orientation = c.orientation,
                   th = p_cyl[1])

    return E

def fields_from_grid(grid, c, inners):
    # grid is expected to be shaped 100, 100, 100, 3
    x, y, z = np.moveaxis(grid, -1, 0)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    #print(points)

    out = []

    for point in points:
        e_val = [_field_step_1(point, cir, inner)
                 for cir, inner in zip(c.children, np.array(inners, dtype=np.float64))]
        out.append(np.sum(np.array(e_val), axis=0))

    out = np.array(out)
    out = np.reshape(out, (100, 100, 100, 3))
    print(out)
    return out

def compute_disk_with_collection(coord, collection:Collection, inners, executor:ThreadPoolExecutor):
    """
    Needs to take in the point (in cartesian space), the collection, and a list of inner_radius values
    and output the E-field (also in cartesian space)
    """
    # combine inners and collection children to a dict so map can iterate over them at the same time


    # GET THE E RHO AND E ZETA
    futures=[executor.submit(_field_step_1, coord, c, inners)
             for c, inners in zip(collection.children, np.array(inners, dtype=np.float64))]

    out = []
    # populate E container with results from each ring (all values are rotated back)
    for future in as_completed(futures):
        out.append(future.result())

    return np.sum(np.array(out), axis=0) # total E = sum by column

import numpy as np
from scipy.constants import epsilon_0

thetas = np.linspace(0, 2 * np.pi, 200)
dtheta = thetas[1] - thetas[0]

def compute_fields(rho, z, Q, O_radius, I_radius=0):
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

    dA = R * dr * dtheta  # area element

    Erho = np.sum(dx / denom * dA)
    Ez   = np.sum(dz / denom * dA)

    E_rho = prefactor * Erho
    E_z   = prefactor * Ez

    return E_rho, E_z

from magpylib import Collection
from concurrent.futures import ThreadPoolExecutor
from Alg.polarSpace import toCyl
from functools import partial
def compute_disk_with_collection(coord, collection:Collection, inners, executor:ThreadPoolExecutor):
    # convert coordinate to cyl
    cyl = toCyl(coord)
    futures = np.empty(len(collection))
    for i in range(len(collection)):
        futures[i]=(executor.submit(compute_fields, rho=cyl[0], z=cyl[2], Q=collection[i].current,
                                       O_radius=collection[i].diameter/2, I_radius=inners[i]))
    out = np.empty((len(collection), 2))
    for i in range(len(futures)):
        out[i]= futures[i].result()

    return np.sum(out, axis=0)


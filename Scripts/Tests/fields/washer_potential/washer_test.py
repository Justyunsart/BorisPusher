import numpy as np
from MakeCurrent import Helmholtz as mirror
from EFieldFJW.washerPhiVectorized import compute_field
import pickle

if __name__ == "__main__":
    # SET UP THE WASHERS
    #   ring location, diameter, current
    collection = mirror(1e-11, 1, 1)
    #   washer inner, outer radius (same for every ring)
    inner_r = 0.1
    outer_r = 0.5
    R_res = 200
    thetas = np.linspace(0, 2 * np.pi, R_res)
    R = np.linspace(inner_r, outer_r, R_res)

    # ITERATE OVER RING IN COLLECTION
    rings = collection.children_all
    rz_res = 200
    Phi = np.empty((rz_res, rz_res, rz_res, 3))
    for i in range(len(rings)):
        print(f"calculating potential for ring {i} of {len(rings)}")

        ring = rings[i]
        # calculate sigma
        sigma_denominator = np.pi * (outer_r ** 2 - inner_r ** 2)
        sigma = ring.current / sigma_denominator  # C/m^2

        # get the r and z to get the gradient for
        sim_lim = np.max(abs(ring.position)) + 0.005
        _r_vals = np.linspace(0.01, 1, rz_res)
        #_z_vals = ring.position[2] -  np.linspace(0.01, sim_lim, rz_res)
        _z_vals =  np.linspace(0.01, sim_lim, rz_res)

        r_vals, z_vals = np.meshgrid(_r_vals, _z_vals, indexing="ij")
        drho = r_vals[1,1] - r_vals[0,1]
        dz = z_vals[1,1] - z_vals[1,0]


        _phi = compute_field(r_vals.ravel(), z_vals.ravel(), sigma, R, drho, dz)
        _phi = np.reshape(_phi, (2, rz_res, rz_res))
        _r, _z = _phi[0], _phi[1]

        # Add the theta column
        # add a new axis
        r3d = _r[:, None, :].repeat(R_res, axis=1)
        z3d = _z[:, None, :].repeat(R_res, axis=1)
        th3d = thetas[None, :, None].repeat(R_res, axis=0).repeat(R_res, axis=2)

        r, th, z = np.stack([r3d, th3d, z3d])

        # convert to cartesian
        X = r * np.cos(th)
        Y = r * np.sin(th)
        cart_grid = np.stack([X, Y, z], axis=-1)
        grid_flat = cart_grid.reshape(-1, 3)

        # rotate by the coil's orientation
        cart_rotated = ring.orientation.apply(grid_flat, inverse=False)
        cart_rotated = cart_rotated.reshape(rz_res, rz_res, rz_res, 3)

        Phi += cart_rotated

    # save the array as a pickled object
    filename = "mirror_washer_potential"
    print(f"saving {filename}.pkl ...")
    with open (f"{filename}.pkl", "wb") as f:
        pickle.dump(Phi, f)

    print(f"finished")
from settings.fields.FieldMethods_Impl import bob_e_impl
from Alg.polarSpace import toCyl, toCart
import numpy as np
from MakeCurrent import Circle as hex
import logging
from pathlib import Path
import os
from definitions import PLATFORM
from magpylib.current import Circle
from magpylib import Collection
from math import isclose

"""
Helper function to ensure background numpy threads complete by running a cheap numpy
operation
"""
def clear_numpy_threads():
    np.array(0).sum()  # complete any numpy background threads

"""
Isolated step of Bob_e solution to see where the numbers diverge across systems
"""
def logged_bob_e_rounding()->None:
    # SET UP THE TESTING ENVIRONMENT
        # Create the debug log file
    def create_debug_log(filename='debug_log.log'):
            # get a path to the logging file
        current_path_dir = Path(__file__).resolve().parent #.../BorisPusher/Scripts/Tests/fields/Bob_e
        # .../BorisPusher/Scripts/Tests/fields/Bob_e/debug/filename.log
        logging_path = os.path.normpath(os.path.join(current_path_dir, os.path.join('debug', filename)))
            # instantiate the logger and the file
        logger = logging.getLogger(__name__)
        logging.basicConfig(filename=logging_path, filemode='w', level=logging.DEBUG, encoding='utf-8')
        logger.info(f"Bob_e logs for system: {PLATFORM}")
        return logger

    # RUN A STEP
    """
    The actual algorithm implementation
    """
    def at(coord, q=1, radius=1, resolution=100, convert=True):
        """
        implementation of the function.
        Inputs:
        q: total charge of the ring in Coulombs
        """
        logger.info("BOB_E FUNCTION CALLED")
        # Parameters
        k = 8.99e9  # Coulomb's constant, N * m^2/C^2
        kq_a2 = (k * q) / (radius ** 2)
        logger.debug(f"kq_a2: {kq_a2}")

        # Coordinate Constants
        if convert:
            coord = toCyl(coord)
        zeta = coord[2] / radius
        rho = coord[0] / radius
        if isclose(rho, 0, abs_tol=1e-10):
            rho = 1e-10
        logger.debug(f"rho: {rho}, zeta: {zeta}")
        # Integral Constants - pg.3 of document
        mag = (rho ** 2 + zeta ** 2 + 1)
        mag_3_2 = mag ** (3 / 2)
        logger.info(f"CALCULATING INTEGRATION SCALARS")
        logger.info("The following are common values used in both zeta and rho scalars")
        logger.debug(f"mag: {mag}, mag_3_2: {mag_3_2}")
        ## Fzeta
        Fzeta_c = (zeta) / (mag_3_2 * (radius ** 2))
        clear_numpy_threads()
        ## Frho
        Frho_c = (rho) / (mag_3_2 * (radius ** 2))
        logger.info("The following are the scalars themselves.")
        logger.debug(f"Fzeta scalar: {Fzeta_c}, Frho scalar: {Frho_c}")
        clear_numpy_threads()

        # Integration
        # Circle is broken into {resolution} slices; with each result being appended to the lists below.
        logger.info("STARTING VECTORIZED INTEGRATION")
        thetas = np.linspace(0, np.pi, resolution,
                             dtype=np.float64)  # np.array of all the theta values used in the integration (of shape {resolution})
        logger.debug(f"thetas: {thetas}")
        cosines = np.cos(thetas)  # np.array of all the cosine values of the thetas
        logger.debug(f"cosines: {cosines}")
        _d = 2 * rho * cosines
        logger.debug(f"d1: 2 * rho * cos(th): {_d}")
        _d1 = _d / mag
        logger.debug(f"d2: d1 / mag: {_d1}")
        denominators = (1 - (_d1)) ** (3 / 2)  # shared denominator values of fzeta and frho
        # replace zeros with a really small decimal.
        denominators[denominators == 0] = 1e-20
        logger.debug(f"denominators: {denominators}")
        clear_numpy_threads()

        logger.info("PERFORMING INTEGRATION EXPRESSION")
        fzeta = 1 / denominators
        clear_numpy_threads()
        frho = (1 - cosines / rho) / denominators
        clear_numpy_threads()
        logger.debug(f"fzeta: {fzeta}")
        logger.debug(f"frho: {frho}")

        # Final - fzeta, frho is summed, multiplied by the integration constant and kq.a^2.
        logger.info("APPLYING SCALAR AND kq_a2")
        zeta_sum = np.asarray(fzeta).sum()
        logger.debug(f"zeta integral: {zeta_sum}")
        zeta_mult_const = zeta * Fzeta_c
        logger.debug(f"zeta integral times scalar: {zeta_mult_const}")
        zeta = zeta_mult_const * kq_a2
        rho = np.asarray(frho).sum() * Frho_c * kq_a2
        logger.debug(f"zeta: {zeta}, rho: {rho}")
        logger.info("BOB_E CALCULATION COMPLETE")
        return zeta, rho


    """
    All of the orientation rotation and translations needed to prepare the cartesian coord.
    to a Bob_e input
    """
    def prepare_coordinate(c:Circle, coordinate:np.ndarray):
        logger.info(f"Preparing coordinate: {coordinate}")
        # ORIENTATION
        # step 1: translate as if the coil center is at origin, then apply coil's inv. rotation
        oriented_cartesian = bob_e_impl.OrientPoint(c, coordinate)
        logger.debug(f"Oriented coordinate in cartesian: {oriented_cartesian}")
        # step 2: convert this oriented coordinate to cylindrical coordinates
        out = toCyl(oriented_cartesian)
        logger.debug(f"Oriented coordinate in cylindrical: {out}")
        clear_numpy_threads()
        logger.info(f"Coordinate preparation complete")
        return out

    def bob_e_step(collection:Collection, coordinate:np.ndarray):
        logger.info(f"STARTING BOB_E LOOP PER CHILD COIL")
        # COLLECT THE E-FIELD VALUES FOR EACH COIL
        _Es = [] # container for the E field values for each coil in the collection (cartesian)
        coil:Circle
        for coil in collection:
                # prepare the input to oriented cylindrical
            oriented_cyl = prepare_coordinate(coil, coordinate)
                # collect input params for the step
            radius = coil.diameter / 2
            Q = coil.current
                # run the step
            logger.info(f"Calculating E for coil: {coil}")
            logger.info(f"position: {coil.position}, radius: {radius}, Q: {Q}, orientation: {coil.orientation}")
            z, r = at(coord=oriented_cyl, q=Q, radius=radius, resolution=100, convert=False)

            logger.info(f"CONVERTING RESULTS BACK TO USABLE FORM")
            logger.info(f"CONVERTING TO CARTESIAN")
                # convert the output back into cartesian
            E_cart = toCart(r, oriented_cyl[1], z) # the theta value is from the input coordinate
            logger.debug(f"coordinate is now: {E_cart}")
            logger.info(f"UNDOING ROTATION")
                # undo the rotation applied to the input coordinates
            out = coil.orientation.apply(E_cart)
            clear_numpy_threads()
            logger.debug(f"E: {out}")
                # append this final output to the _Es list
            _Es.append(out)
        logger.info(f"BOB_E LOOP FINISHED")
        logger.debug(f"E-field for each coil in collection: {_Es}")
        # SUM THE E-FIELD VALUES BY COLUMN TO GET THE FINAL RESULT
        E_sum = np.sum(np.array(_Es), axis=0)
        clear_numpy_threads()
        logger.debug(f"columnwise sum: {E_sum}")
        logger.info("FINISHED STEP")

        # Create the debug logger
    logger = create_debug_log()
        # Create the bob inputs (coil, particle position)
    collection = hex(dia=1.7, a=1e-11, d=1.1, gap=0)  # hexahedron config with 100K Amps, 1.7 diameter, 1.1m offset
    particle = np.zeros(3)  # (0,0,0): particle is at the origin
        # run the step
    bob_e_step(collection, particle)


if __name__ == "__main__":
    logged_bob_e_rounding()
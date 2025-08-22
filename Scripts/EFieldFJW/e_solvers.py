import numpy as np
from scipy.constants import epsilon_0
from scipy.spatial.transform import Rotation
from Alg.polarSpace import toCyl, toCart

"""
Second attempt at polymorphism for field solvers with classes.
First attempt was in settings.fields.FieldMethods_Impl.py, and the reason(s) why it didn't work was:
    - coupled widgets and parameter handing with holding analytic solution.

This time, classes will only organize functions. All handling of parameters and widgets are from elsewhere.
"""
##################
# ABSTRACT CLASS #
##################
from abc import ABC, abstractmethod
# CLASS FOR HOLDING FUNCTION
class Solver(ABC):
    """
    Abstract base class for solvers.
    """
    @abstractmethod
    def solve(self, params : dict):
        """
        Compute results with a parameter dictionary input.
        There are some assumptions about the output format to make it work for polymorphism:
            1. Inputs can can range from single to multiple coordinates.
            2. Single coord output is shape 3, multiple coord. output is shape (n, 3)
        """

# SOLVER MODULES
################
# Specific methods can pick and choose which module to inherit from.
# This would allow solvers to share the same function implementation for common operations.
# It also is a good way to label the needs/type of the solver for the developer
class RotationSolver:
    """
    Module for solvers that need functions for rotations of both field and input coordinates.
    Usually done if the solver requires reorientations in object space.
    """
    @staticmethod
    def orient_point_to_coil(coord, rotation:Rotation, position):
        # always assume coord input is shaped like: (n, n, 3)
        original_shape = coord.shape


        # function expects shape (m, 3), so we need to reshape
        reshaped_coord = coord.reshape(-1, 3)
        rotated_coord = rotation.apply(reshaped_coord - position, inverse=True) #(m, 3)

        # after applying rotation, put shape back to original
        rotated_coord = rotated_coord.reshape(original_shape)

        return rotated_coord

    @staticmethod
    def orient_point_to_world(coord, rotation:Rotation, output_shape:tuple=None):
        # always assume input is (m, 3)
        rotated_coord = rotation.apply(coord, inverse=False)

        # if an output shape is not explicitly defined, the output will have the matching (m, 3) input shape.
        if output_shape is None:
            return rotated_coord

        # if it is defined, then the output happens after a reshape.
        return rotated_coord.reshape(output_shape)

class CylindricalSolver:
    """
    Module for solvers that expect cylindrical coordinate inputs.
    Since rotation functions expect cartesian, these methods require conversion functionality if they need
    to do so.

    **Remember that converting to cart. before calling rotation funcs is not strictly enforced, so it is on u.
    """
    @staticmethod
    def cartesian_to_cylindrical(x, y, z):
        """
        Convert Cartesian (x, y, z) -> Cylindrical (r, phi, z).

        Works on scalars or NumPy arrays.
        phi is in radians.
        """
        x, y, z = np.asarray(x), np.asarray(y), np.asarray(z)
        r = np.sqrt(x ** 2 + y ** 2)
        phi = np.arctan2(y, x)
        return r, phi, z
    @staticmethod
    def cylindrical_to_cartesian(r, phi, z):
        """
        Convert Cylindrical (r, phi, z) -> Cartesian (x, y, z).

        Works on scalars or NumPy arrays.
        phi is in radians.
        """
        r, phi, z = np.asarray(r), np.asarray(phi), np.asarray(z)
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        return x, y, z

class RotationAndCylindricalSolver(RotationSolver, CylindricalSolver):
    """
    Handles converting to cart. before rotation, and converting to cyl. after rotation.
    """
    @staticmethod
    def prepare_coords_inverse(coords, rotation:Rotation, position):
        """
        Rotates the given cartesian coordinates by the inverse rotation of the provided rotation object.
        Then converts rotated results to cylindrical coordinates.

        coords: (n,n,n,3) of field point coordinates.
        rotation: a scipy.spatial.transform.Rotation object.
        """
        rotated_coords = RotationSolver.orient_point_to_coil(coords, rotation, position) #if coord = (n,n,3); so is this output
        rotated_coords = np.moveaxis(rotated_coords, -1, 0) #convert to (3,n,n) to unpack for
        r, phi, z = CylindricalSolver.cartesian_to_cylindrical(*rotated_coords)
        converted_coords = np.stack([r, phi, z], axis=0) #(3,n,n)
        return converted_coords
#----------#

#################
# INSTANTIATION #
#################
class Bob_e_Solver(Solver, RotationAndCylindricalSolver):
    def solve(self, params : dict):
        """
        Calls an internal single-coil solver (that assumes cyl. coords in aligned space) from an input of:
        {
            coord: (3, n, n, n),
            collection: mp.Collection
        }
        """
        # Unpack input dictionary
        coord = params.get('coord')
        collection = params.get('collection')

        def bob_e_at(coord, rotation, q=1, radius=1, resolution=200):
            """
            GIVES FIELD FOR ONE COIL
            Vectorized version of bob_e_at with proper numerical integration.
            Inputs:
                coord: ndarray of shape (3, Nx, Ny, Nz) in cylindrical coordinates (r, θ, z)
                rotation: the coil's orientation (scipy.spatial.transform.Rotation object)
                q: total charge
                radius: coil radius
                resolution: number of integration points
            Returns:
                zeta, rho: electric field components along z and r directions, shape (Nx, Ny, Nz)
            """
            # PREPARE INPUTS #
            ##################
            k = 8.99e9  # Coulomb's constant
            kq_a2 = (k * q) / (radius ** 2)

            # make cyl-coord inputs non-dimensional
            # Extract components along first axis
            rho = coord[0] / radius  # shape: (...), can be 1D, 2D, or 3D
            phi = coord[1] / radius
            zeta = coord[2] / radius


            # CALCULATE FIELD #
            ###################
            mag = rho ** 2 + zeta ** 2 + 1
            mag_3_2 = mag ** 1.5

            Fzeta_c = zeta / (mag_3_2 * radius ** 2)
            Frho_c = rho / (mag_3_2 * radius ** 2)

            # Integration setup
            thetas = np.linspace(0, np.pi, resolution)
            dtheta = thetas[1] - thetas[0]
            cosines = np.cos(thetas).reshape((-1, 1, 1, 1))  # (res, 1, 1, 1)

            # Broadcast spatial coords
            rho_exp = np.expand_dims(rho, axis=0)  # always adds a new leading axis
            mag_exp = np.expand_dims(mag, axis=0)

            denom = (1 - (2 * rho_exp * cosines / mag_exp)) ** 1.5
            denom = np.where(denom == 0, 1e-20, denom)

            # Safe rho to avoid div-by-zero
            rho_safe = np.where(np.abs(rho_exp) < 1e-8, 1e-8, rho_exp)

            # Integrate
            fzeta = np.sum((1 / denom) * dtheta, axis=0)
            frho = np.sum(((1 - cosines / rho_safe) / denom) * dtheta, axis=0)

            # Scale
            E_zeta = fzeta * Fzeta_c * kq_a2
            E_rho = frho * Frho_c * kq_a2

            # CLEANING #
            ############
            # Convert results back to Cartesian
            x, y, z = self.cylindrical_to_cartesian(E_rho, phi, E_zeta)
            # Re-align the results back to world space by applying forward rotation of coil to results
            e_coords = np.stack([x, y, z], axis=-1) #(n,n,3)
            e_coords_rehsaped = e_coords.reshape((-1, 3)) #scipy.rotate expects (n, 3)
            e_coords_aligned = self.orient_point_to_world(e_coords_rehsaped, rotation, output_shape=e_coords.shape)

            return e_coords_aligned

        # OBJECTIVE:
        #   call bob_e_at for each coil in the collection (provided that rotations are done for each)
        #   then sum all results by axis to get total field.
        e_sum = np.zeros_like(coord)
        for coil in collection:
            #print(coil.position)
            # GATHER PARAMETERS #
            #####################
            rotation = coil.orientation
            q = coil.current
            radius = coil.diameter / 2

            # PREPARE COORDINATE INPUT #
            ############################
            # fyi: coordinates are expected to be (n,n,3) and cartesian at this point.
            # Align points to coil space, then convert to cylindrical coords.
            aligned_cyl_input = self.prepare_coords_inverse(coord, rotation, coil.position)

            # COLLECT AND AGGREGATE RESULTS #
            #################################
            e_coil = bob_e_at(aligned_cyl_input, rotation, q, radius, resolution=100) #(n,n,3)
            e_sum += e_coil[0]
        return e_sum

class Disk_e_Solver(Solver):
    def solve(self, params : dict):
        # Collect params
        def compute_fields(rho, z, Q, O_radius, I_radius=0, orientation=None, th=0):
            thetas = np.linspace(0, 2 * np.pi, 200)
            dtheta = thetas[1] - thetas[0]
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
            dx = rho - x  # shape (200, 200)
            dy = -y
            dz = z

            denom = (dx ** 2 + dy ** 2 + dz ** 2) ** 1.5 + 1e-20  # Avoid division by zero

            dA = R * dr * dtheta  # area element

            Erho = np.sum(dx / denom * dA)
            Ez = np.sum(dz / denom * dA)

            E_rho = prefactor * Erho
            E_z = prefactor * Ez

            # FORMAT OUTPUT
            # convert result back to cartesian
            E_raw = toCart(E_rho, th, E_z)
            # apply forward rotation
            E = orientation.apply(E_raw, inverse=False)

            return E

        def _field_step_1(coord, c, inners):
            # orient point
            p_oriented = c.orientation.apply(coord - c.position, inverse=True)
            # convert coordinate to cyl
            p_cyl = toCyl(p_oriented)

            E = compute_fields(rho=p_cyl[0], z=p_cyl[2],
                               Q=c.current,
                               O_radius=c.diameter / 2,
                               I_radius=inners,
                               orientation=c.orientation,
                               th=p_cyl[1])

            return E



class Washer_Potential_e_Solver(Solver):
    def solve(self, params : dict):
        def compute_washer_potential(rho_vals, z_vals, Q, inner_r, outer_r, res=400):
            """
            grid: array, (2,n): either one point or a meshgrid, representing (rho, phi, zeta) to calc at.
            """
            sigma = Q / (np.pi * (outer_r ** 2 - inner_r ** 2))  # charge density C/m^2
            prefactor = sigma / (4 * np.pi * epsilon_0)

            # Create a meshgrid for r and theta (used in integration)
            r_vals = np.linspace(inner_r, outer_r, res)
            theta_vals = np.linspace(0, 2 * np.pi, res)
            dr = r_vals[1] - r_vals[0]
            dtheta = theta_vals[1] - theta_vals[0]

            r, theta = np.meshgrid(r_vals, theta_vals, indexing='ij')  # shape: (Nr, Ntheta)

            # Precompute differential area element dA
            dA = r * dr * dtheta  # shape: (Nr, Ntheta)

            # Precompute x and y coordinates of source points in the integration plane
            x_src = r * np.cos(theta)  # shape: (Nr, Ntheta)
            y_src = r * np.sin(theta)

            Phi = np.empty(rho_vals)
            for i in range(len(rho_vals)):
                for j in range(len(z_vals)):
                    rho = rho_vals[i]
                    z = z_vals[j]

                    # Distance from (rho, 0, z) to each source point (x_src, y_src, 0)
                    dx = rho - x_src
                    dy = -y_src
                    dz = z

                    Denom = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2) + 1e-20  # avoid division by zero

                    integrand = dA / Denom  # shape: (Nr, Ntheta)

                    Phi[j, i] = prefactor * np.sum(integrand)
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

#from EFieldFJW.analyticEfield3 import ax
from EFieldFJW.e_solvers import Solver
from mpl_toolkits.axes_grid1 import make_axes_locatable
"""
Classes for graphing logic with solvers.
"""

# GENERAL CLASS FOR HOLDING GRAPHING LOGIC
class SolverUtils:
    @staticmethod
    def generate_xz_coords(lim=3, resolution=200):
        """
        Generates and outputs a meshgrid of points that represent a 2D cross-section of the simulation space.
        Because this cross-section will always be the XZ plane at Y = 0, the creation script is going to
        specialize for doing that.

        y = 0 = r * sin * Phi -> Phi is either 0 or pi depending on x's sign.

        output shape: (n, n, 3)
        """

        x = np.linspace(-lim, lim, resolution)
        z = np.linspace(-lim, lim, resolution)
        X, Z = np.meshgrid(x, z, indexing="ij")
        Y = np.ones_like(X) * 0

        return np.stack([X, Y, Z], axis=-1)

# ABSTRACT CLASS FOR THE GRAPHER CLASS, WHICH WILL BE MADE FOR EACH SOLVER.
class Grapher(ABC):
    """
    Abstract base class for solver graphers.
    One needs to exist for each solver method that you want to be able to create
    diagnostic graphs for.

    The matplotlib figure and plot involved in the graphing functions are expected
    to be provided upon instantiation!
    """
    def __init__(self, solver:Solver, collection, field='E', **kwargs):
        """
        solver: an instance of the Solver ABC defined in EFieldFJW.e_solvers.
            - holds the actual implementation to get field vals from.
        """
        self.solver = solver
        self.collection = collection
        self.lim = np.max(np.abs(self.collection[0].position)) + 0.5 #extend half a meter from the edges
        self.__dict__.update(kwargs) #add any unique params needed to instance attributes
        self.coords = None #populated when the grapher is gathering its own params.
        self.linspace_res = 100 #directly used in generating the coordinates

        # LABEL ATTRIBUTES
        # since these will always graph the XZ axis, the X and Y labels for the 2D plot are known quantities.
        self.xlabel = "X-axis"
        self.ylabel = "Z-axis"

        self.field = field

    @abstractmethod
    def gather_params(self)->dict:
        """
        This method should return a dict of solver parameters that would return the
        cross-section field data.
        """
        pass

    def gather_data(self):
        """
        This method should return the field data.
        """
        return self.solver.solve(self.gather_params())

    @staticmethod
    def _unpack_data_and_coords(data, coords):
        """
        Assumes that both 'data' and 'coords' are shaped (n,n,3), and correspond to each other.
        """

        X, Y, Z = np.moveaxis(coords, -1, 0)  # unpack coordinates
        Fx, Fy, Fz = np.moveaxis(data, -1, 0)  # unpack field

        F_norm = np.linalg.norm(data, axis=-1)

        return X, Y, Z, Fx, Fy, Fz, F_norm

    @staticmethod
    def set_graph_vis_standard_options(fig:plt.figure, plot:plt.axis):
        """
        Provide this function a matplotlib figure and axis instance.
        When filling that graph with the selected information, the settings defined
        here will also apply to it.
        """
        plot.grid(True)
        fig.set_size_inches(5,5)
        fig.tight_layout()
        plot.set_aspect('equal')

    def graph_streamline(self, instance, method, cmap='viridis'):
        """
        Using solver-produced data, create a streamline plot with a cmap and cbar.

        'data' : a numpy array with shape (n,n,n,3), populated by field
        values. 'data' should also be oriented in the world space, and be in cartesian coordinates.

        'coords' : a numpy array with the shape (n,n,n,3), represents the cartesian coordinates that correspond to
        the field values in 'data'
        """
        data = self.gather_data()
        X, Y, Z, Fx, Fy, Fz, F_norm = self._unpack_data_and_coords(data, self.coords)
        plot = instance.plot
        fig = instance.fig

        stream = instance.plot.streamplot(np.array(X)[:,0], np.array(Z)[0,:],
                                   np.array(Fx).T, np.array(Fz).T,
                                   color=np.log(F_norm + 1e-20), #assume data.shape = (n,n,3)
                                   density=1,
                                   cmap=cmap)

        divider = make_axes_locatable(plot)
        cax = divider.append_axes("right", size='5%', pad=0.05)

        instance.cb = fig.colorbar(stream.lines, cax=cax, label=f"{self.field} mag. log norm")

        # FORMATTING #
        ##############
        title = f"{self.field} Streamline From Solver {method}"
        plot.set_title(title)
        plot.set_xlabel(self.xlabel)
        plot.set_ylabel(self.ylabel)


    def graph_contour(self, instance, method,field="E", levels=100, cmap='turbo'):
        """
        Using solver-produced data, create a contour plot with a cmap and cbar.

        'data' : a numpy array with shape (n,n,n,3), populated by field
        values. 'data' should also be oriented in the world space, and be in cartesian coordinates.

        'coords' : a numpy array with the shape (n,n,n,3), represents the cartesian coordinates that correspond to
        the field values in 'data'
        """
        data = self.gather_data()
        X, Y, Z, Fx, Fy, Fz, F_norm = self._unpack_data_and_coords(data, self.coords)
        plot = instance.plot
        fig = instance.fig

        contour = instance.plot.contourf(
            X, Z, F_norm,
            levels=levels,
            cmap=cmap
        )
        divider = make_axes_locatable(plot)
        cax = divider.append_axes("right", size='5%', pad=0.05)

        instance.cb = fig.colorbar(contour, cax=cax, label=f"{field} mag. log norm")

        # FORMATTING #
        ##############
        title = f"{field} Contour From Solver {method}"
        plot.set_title(title)
        plot.set_xlabel(self.xlabel)
        plot.set_ylabel(self.ylabel)

#----------#

#################
# INSTANTIATION #
#################
class Bob_e_Grapher(Grapher):
    def gather_params(self):
        """
        This method should return a dict of solver parameters for XZ plane:
            - coord: (3, n, n, n) array in cylindrical coordinates
                > But because this needs rotation before cyl. space conversion,
                  this function will provide the cartesian world space coordinates only.
            - q: charge, in Coulombs
            - radius: coil's radius, in meters
            - resolution: number of points in integration

        Because that solver is single-coil, there is an extra layer of looping that
        extracts the q and radius from each coil, transforms the input coordinates, then
        adds the results from each coil.

        Therefore, this func. only needs to return a dict where:
        {
            coord: (3, n, n, n),
            collection: mp.Collection
        }
        """
        # Gather the cart. cross-section coordinates.
        self.coords = SolverUtils.generate_xz_coords(resolution=self.linspace_res, lim=self.lim)
        return {'coord': self.coords, 'collection':self.collection}

class Disk_e_Grapher(Grapher):
    def gather_params(self):
        self.coords = SolverUtils.generate_xz_coords(resolution=self.linspace_res, lim=self.lim) #shape: (n,n,3)
        _x, _y, _z = np.moveaxis(self.coords, -1, 0)
        points = np.stack([_x.ravel(), _y.ravel(), _z.ravel()], axis=-1)


        return{
            'coords' : points,
            'collection' : self.collection,
            'inners' : self.inners
        }
    def gather_data(self):
        Es = self.solver.solve(self.gather_params())
        # the results are [m, 3], and we need them back into the original order

        _x = Es[:, 0].reshape(self.linspace_res, self.linspace_res)
        _y = Es[:, 1].reshape(self.linspace_res, self.linspace_res)
        _z = Es[:, 2].reshape(self.linspace_res, self.linspace_res)

        return np.stack([_x, _y, _z], axis=-1)
class Washer_Potential_e_Grapher(Grapher):
    def gather_params(self):
        """
        Outputs whatever you need to get the field data of the assumed initial conditions of the xz plane.

        Notes:
            Inputs for the washer solver:
                - rho_vals, z_vals : the field coordinates to calculate for
                - Q : charge of the ring
                - inner_r : washer's inner radius
                - outer-r : washer's total radius
                - res : the number of points to use in the internal linspace.
        """
        self.coords = SolverUtils.generate_xz_coords(resolution=self.linspace_res, lim=self.lim) #shape: (n,n,3)

        _x, _y, _z = np.moveaxis(self.coords, -1, 0)
        points = np.stack([_x.ravel(), _y.ravel(), _z.ravel()], axis=-1)

        # collect coil information
        normals = []  # input n_coils amount of (3,) arrays
        sigmas = []  # input n_coils amount of empty lists
        for ring in self.collection.children_all:
            # we can get the coil's normal by rotating [0, 0, 1] by the coil's orientation.
            default_z = np.array([0, 0, 1])
            normals.append(ring.orientation.apply(default_z))

            # append empty list per coil into sigmas
            sigmas.append([])

        return {
            "points" : points,
            "collection" : self.collection,
            "inners" : self.inners,
            "normals" : normals,
            "sigmas" : sigmas,
        }

    def gather_data(self):
        """
        because the potential solver's solve method only gives the potential,
        we need to do some extra work before getting usable field values.
        """
        # Gather the potential
        potential = self.solver.solve(self.gather_params()).reshape(self.linspace_res, self.linspace_res)

        # Also gather the slope of axis
        dax = self.coords[1,0,0] - self.coords[0,0,0] #slope of x axis = slope of z axis (assumed)

        dphi_dx, dphi_dz = np.gradient(potential, dax, dax)
        Ex = -dphi_dx
        Ey = np.zeros_like(Ex)
        Ez = -dphi_dz

        return np.stack([Ex, Ey, Ez], axis=-1) #y-axis=0, since we cannot calculate potential for it (as cross-section)

class MagpyGrapher(Grapher):
    field = 'B'
    def gather_params(self) ->dict:
        self.coords = SolverUtils.generate_xz_coords(resolution=self.linspace_res, lim=self.lim) #shape: (n,n,3)
        _x, _y, _z = np.moveaxis(self.coords, -1, 0)
        points = np.stack([_x.ravel(), _y.ravel(), _z.ravel()], axis=-1)

        return{
            'coords' : points,
            'collection' : self.collection
        }
    def gather_data(self):
        data = self.solver.solve(self.gather_params())
        # results are (m, 3). need to reshape back to expected shape
        _x = data[:, 0].reshape(self.linspace_res, self.linspace_res)
        _y = data[:, 1].reshape(self.linspace_res, self.linspace_res)
        _z = data[:, 2].reshape(self.linspace_res, self.linspace_res)

        return np.stack([_x, _y, _z], axis=-1)

"""
All the logic that goes inside the FieldMethods.py's enums themselves.
I decided that having all the implementations in one place makes it easy to add more methods in the future.
It's also easier to debug and change parameters globally when testing different functionalities. 
"""
import os
from Gui_tkinter.funcs.GuiEntryHelpers import LabeledEntry
from Alg.polarSpace import toCyl
import tkinter as tk
import numpy as np
import concurrent.futures
from magpylib.current import Circle
from Gui_tkinter.widgets.Bob_e_Circle_Config import Bob_e_Circle_Config
from definitions import DIR_ROOT, NAME_BOB_E_CHARGES, NAME_INPUTS
from settings.configs.funcs.config_reader import runtime_configs
from Alg.polarSpace import toCyl, toCart

##############
# BASE CLASS #
##############
class FieldMethod():
    """
    Abstract class for frontend and backend links for each field method.
    Contains the actual equation, as well as the ability to extract parameter values from its GUI widgets.
    """
    autoUpdate = True # flag for whether the graph should update whenever it's chosen.
    def __init__(self, master, widget, root=None):
        self.widget = widget(master, root)
    # Called when the GUI wants to display the field with its current values.
    def graph(self, plot, fig, lim, collection=None, *args):
        pass
    # Toggles to either show or remove its widgets for when the method is selected/deselected.
    def ShowWidget(self):
        self.widget.ShowWidget()
    def HideWidget(self):
        self.widget.HideWidget()    
    # When the program wants to extract the parameter values, it calls this.
    def GetData(self):
        pass
    # When you want to force the widget to populate a given value, you can call this.
    def Set(self, key, value):
        pass

class field_impl():
    """
    Abstract class for the GUI link to the fieldMethod.
    Contains the tkinter widgets involved.
        > They are all encapsulated in its own class so the program can generalize function calls
          for common operations (toggle widget visibility)
    """
    listeners = []
    widgets = []
    frame1:tk.Frame = None
    widget_frames = []

    def __init__(self, main):
        self.add_listener(main)
    # Some observer methods to handle basic event handling
    def add_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)
    def trigger_listener(self, *args):
        for listener in self.listeners:
            listener.update()
    # Toggle associated widgets on/off for when the method is selected/deselected.
    def ShowWidget(self):
        for frame in self.widget_frames:
            frame.grid()
            self.trigger_listener()
        #self.frame1.grid()
    def HideWidget(self):
        for frame in self.widget_frames:
            frame.grid_remove()
            self.trigger_listener()
        #self.frame1.grid_remove()
        

################
# GUI WIDGETS #
###############
"""
Houses instances of the field_impl class for each field method.
"""
class Fw_widget(field_impl):
    def __init__(self, frame, main=None):
        super().__init__(main)
        self.root = main
        self.frame1 = tk.Frame(frame)
        self.widget_frames = [self.frame1]
        self.frame1.grid(row=2, column=0)
        self.A = LabeledEntry(self.frame1, .1, row=1, col=0, title="A: ", width=10)
        self.B = LabeledEntry(self.frame1, .1, row=1, col=4, title="B: ", width=10)
        self.widgets = [self.A, self.B]
        
        self.A.value.trace_add("write", self.trigger_listener)
        self.B.value.trace_add("write", self.trigger_listener)
    

class Zero_widget(field_impl):
    def __init__(self, frame, main=None):
        super().__init__(main)
        self.root = main
        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)
        self.widget_frames = [self.frame1]
        self.X = LabeledEntry(self.frame1, 0, row=1, col=0, title="X: ", width=5, state="readonly")
        self.Y = LabeledEntry(self.frame1, 0, row=1, col=4, title="Y: ", width=5, state="readonly")
        self.Z = LabeledEntry(self.frame1, 0, row=1, col=8, title="Z: ", width=5, state="readonly")
        self.widgets = [self.X, self.Y, self.Z]

class Bob_e_widget(field_impl):
    def __init__(self, frame, main=None):
        super().__init__(main)
        self.root = main
        # To make the graph function only work with the provided button, flag it to not update.
        self.autoUpdate = False

        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)
        self.frame2 = tk.Frame(frame)
        self.frame2.grid(row=3, column=0)

        self.widget_frames = [self.frame1, self.frame2]

        #self.q = LabeledEntry(self.frame1, .1, row=1, col=0, title="q: ", width=10)
        self.res = LabeledEntry(self.frame1, 100, row=1, col=1, title="res: ", width=10)
        # Button to call configuration table.
        #self.buttonFrame = tk.Frame(frame)
        #self.graphButton = tk.Button(self.frame1, text="Config Circle")
        #self.graphButton.grid(row=1, col=0)
        #self.buttonFrame.grid(row=3, column=0)
        #self.graphButton.pack()

        # Coil Config
        self.table = Bob_e_Circle_Config(self.frame2,
                                         dir=os.path.join(runtime_configs['Paths']['inputs'], NAME_BOB_E_CHARGES))
        self.widgets = [self.table, self.res]
        self.table.grid(row=0)

        #self.q.value.trace_add("write", self.trigger_listener)
        self.res.value.trace_add("write", self.trigger_listener)

    def ShowWidget(self):
        super().ShowWidget()
        #self.buttonFrame.grid()

    def HideWidget(self):
        super().HideWidget()
        #self.buttonFrame.grid_remove()
    
    

##################
# IMPLEMENTATION #
##################
"""
Contains the FieldMethod class instances for each field method.
"""
class Fw_impl(FieldMethod):
    def __init__(self, master, root, widget=Fw_widget):
        super().__init__(master, widget, root)
    
    def at(coord, A, B):
        """
        Function to contain the actual implementation.
        Called when the program wants to use the function to get a value.
        For example, magpy4c1.py when it wants to get the E-field at a coordinate.

        All the values are externally provided.

        Inputs:
        - coord: a single int/float. It is expected that axis handling is done externally.
        - A, B: method-specific variables externally provided.
        
        Output:
        - A single digit representing the E magnitude for the input coordinate.
        """
        return np.multiply(A * np.exp(-(coord / B)** 4), (coord/B)**15)


    
    def graph(self, plot, fig, lim, *args, **kwargs):
        try:
            #print(f'A is: {self.A.value.get()}')
            #print(f'B is: {self.B.value.get()}')
            #print(f'Lim is: {lim}')
            A = float(self.widget.A.value.get())
            B = float(self.widget.B.value.get())

            lim = abs(lim)
            glim = 1.5 * lim
            x = np.linspace(-glim, glim, 50)
            # equation for fw_E
            E = np.multiply(A * np.exp(-(x / B)** 4), (x/B)**15)
            #print(f'X axis is: {x}')
            #print(f'Y axis is: {E}')
            plot.plot(x,E)
            
            # also plot vertical lines for where the coils are, for visual clarity
            plot.axvline(x = lim, color='r', linestyle='dashed')
            plot.axvline(x = -lim, color='r', linestyle='dashed')

        except ValueError:
            pass
    def GetData(self):
        return {"Fw" : 
                {"A" : self.widget.A.value.get(),
                "B" : self.widget.B.value.get()}}
    def Set(self, key, value):
        if key == "A":
            self.widget.A.value.set(value)
        elif key == "B":
            self.widget.B.value.set(value)


class Zero_impl(FieldMethod):
    def __init__(self, master, root, widget=Zero_widget):
        super().__init__(master, widget, root)
    
    def graph(self, plot, fig, lim, *args):
        plot.axhline(y=0, color='b')

    def GetData(self):
        return {"Zero" : 0}

class bob_e_impl(FieldMethod):
    autoUpdate = True
    def __init__(self, master, root, widget=Bob_e_widget):
        super().__init__(master, widget, root)
        # register the graph button to the graphing function

    
    def at(coord, q=1, radius=1, resolution=100, convert=True):
        """
        implementation of the function.
        Inputs:
        q: total charge of the ring in Coulombs
        """
        #print(f"q is: {q}")
        #print(f"coord is: {coord}")
        #print(f'FieldMethods_Impl.bob_e_impl.at: bob_e called with charge {q} and radius {radius}')
        # Parameters
        k = 8.99e9 # Coulomb's constant, N * m^2/C^2
        kq_a2 = (k * q)/(radius**2)

        # Coordinate Constants
        if convert:
            coord = toCyl(coord)
        zeta = coord[2] / radius
        rho = coord[0] / radius
        if rho == 0:
            rho = 0.00001
        r1 = rho

        # Integral Constants - pg.3 of document
        mag = (rho ** 2 + zeta ** 2 + 1)
        mag_3_2 = mag ** (3/2)
        ## Fzeta
        Fzeta_c = (zeta)/(mag_3_2 * (radius ** 2))
        ## Frho
        Frho_c = (rho)/(mag_3_2 * (radius ** 2))

        # Integration
        # Circle is broken into {resolution} slices; with each result being appended to the lists below.

        thetas = np.linspace(0, np.pi, resolution, dtype=np.float64) # np.array of all the theta values used in the integration (of shape {resolution})
        cosines = np.cos(thetas) # np.array of all the cosine values of the thetas
        denominators = (1-((2 * rho * cosines)/mag)) ** (3/2) # shared denominator values of fzeta and frho
        
        # replace zeros with a really small decimal.
        denominators[denominators==0] = 1e-20

        fzeta = 1/denominators
        frho = (1 - cosines / rho) / denominators

        # Final - fzeta, frho is summed, multiplied by the integration constant and kq.a^2.
        zeta = np.asarray(fzeta).sum() * Fzeta_c * kq_a2
        rho = np.asarray(frho).sum() * Frho_c * kq_a2
        return zeta, rho
    
    def GetData(self):
        return {"Bob_e":
                {
                    "res": self.widget.res.value.get(),
                    "collection": self.widget.table.get_collection()
                    }
                }
    
    def Set(self, key, value):
        if key == "res":
            self.widget.res.value.set(value)

    def graph(self, plot, fig, lim, cax, *args):
        """
        When called, will populate the given plot with 
        a contour of the field mags (sum of the zeta, rho components.)
        """
        data = self.GetData()["Bob_e"]

        # Before doing anything, set the axis labels.
        plot.set_xlabel("X-axis")
        plot.set_ylabel("Z-axis")
        plot.set_title("E field mag. on the X-Z plane")

        # Resolution parameters - determines fidelity of graph
        resolution = 100 # determines the number of points created between the bounds
        
        lim = lim + 1

        ## Construct grid
        x_linspace = np.linspace(-lim, lim, resolution)
        y_linspace = np.zeros(1)
        z_linspace = np.linspace(-lim, lim, resolution)

        grid = np.array(np.meshgrid(x_linspace, y_linspace, z_linspace, indexing='ij')).T
        #points = np.column_stack(np.vstack([gX.ravel(), z_linspace, gY.ravel()]))
        grid = np.moveaxis(grid, 1, 0)[0]
        X, Y, Z = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)
        points = grid.reshape(100 ** 2, 3)
        # For every point, for every coil, orient the point and plug it in the function.

        z_data = bob_e_impl.fx_calc(points, data["collection"], int(data["res"]))

        sum_Z = np.log(np.array(z_data)).reshape(resolution, resolution)
        smesh = plot.contourf(X, Z, sum_Z, levels=100,
                                cmap="turbo")
        
        # Colorbar checking
        last_axis_label = fig.axes[-1].get_label() # colorbar is assumed to be the last added axis. So we check the last axis label for existing colorbars.
        #print(fig.axes[-1].get_label())
        cb = fig.colorbar(smesh, cax=cax)

    
    def fx_calc(points, coils, r):
        #print(points)
        #print(coils)
        sums = []
        results = []

        for point in points:
            sum, _ = bob_e_impl._ecalc(point, coils, r)
            sums.append(sum)

        #with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #    futures = {executor.submit(bob_e_impl._ecalc, point, coils, r): point for point in points}
        #    #print(len(futures))
        #
        #    for index, task in enumerate(futures):
        #        result = task.result()
        #        #print(result)
        #        sum.append(result[0])

        return sums

    
    def _ecalc(point, collection, res, sums=True):
        """
        wrapper to orient the point for each coil in the collection, and to call the integration for that point.
        """
        out = []
        transformed=None
        for c in collection.children_all:
            _transformed = bob_e_impl.OrientPoint(c, point)
            transformed = toCyl(_transformed)
            #print(f'{_transformed} became {transformed}')
            z, r = bob_e_impl.at(coord=transformed, radius = (c.diameter/2), convert=False, q=c.current, resolution=res)
            #sums.append(z + r)
                # apply rotation back to the thing to restore context
            cart = toCart(r, transformed[1], z)
            cart = c.orientation.apply(cart)
            out.append(cart)
        _sum = np.sum(out, axis=0)
        if sums:
            _sum=np.linalg.norm(_sum)
            #print(f"point: {point}, sum: {sum}, rect: {rect}")

        #print(_sum)
        return _sum, transformed

    
    def OrientPoint(c:Circle, point):
        """
        Points plugged into the self.at function need to be transformed to be in the assumed config.
        """
        # Reset rotation to identity
        rotation = c.orientation
        #print(f"coil rotation: {rotation.as_euler('xyz', degrees=True)}")
        # subtract the coil's position from the rotated point to make it centered at the origin.
        p = point - c.position
        # after subtracting, the rotation then can be applied. This makes the point rotate about the coil center.
        inv_rotation = rotation.inv()
        rotated_point = inv_rotation.apply(p)


        #print(f"started with {point}, ended with {rotated_point}")
        return rotated_point
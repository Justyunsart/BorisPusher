"""
All the logic that goes inside the FieldMethods.py's enums themselves.
I decided that having all the implementations in one place makes it easy to add more methods in the future.
It's also easier to debug and change parameters globally when testing different functionalities. 
"""
from GuiEntryHelpers import LabeledEntry
from Alg.polarSpace import toCyl
import tkinter as tk
from tkinter import ttk
import numpy as np
import concurrent.futures
from magpylib.current import Circle
from scipy.spatial.transform import Rotation as R
from matplotlib import pyplot as plt

##############
# BASE CLASS #
##############
class FieldMethod():
    """
    Abstract class for frontend and backend links for each field method.
    Contains the actual equation, as well as the ability to extract parameter values from its GUI widgets.
    """
    autoUpdate = True # flag for whether the graph should update whenever it's chosen.
    def __init__(self, master, widget):
        self.widget = widget(master)
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
    # Some observer methods to handle basic event handling
    def add_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)
    def trigger_listener(self, *args):
        for listener in self.listeners:
            listener.update()
    # Toggle associated widgets on/off for when the method is selected/deselected.
    def ShowWidget(self):
        self.frame1.grid()
    def HideWidget(self):
        self.frame1.grid_remove()
        

################
# GUI WIDGETS #
###############
"""
Houses instances of the field_impl class for each field method.
"""
class Fw_widget(field_impl):
    def __init__(self, frame):
        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)
        self.A = LabeledEntry(self.frame1, .1, row=1, col=0, title="A: ", width=10)
        self.B = LabeledEntry(self.frame1, .1, row=1, col=4, title="B: ", width=10)
        self.widgets = [self.A, self.B]
        
        self.A.value.trace_add("write", self.trigger_listener)
        self.B.value.trace_add("write", self.trigger_listener)
    

class Zero_widget(field_impl):
    def __init__(self, frame):
        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)
        self.X = LabeledEntry(self.frame1, 0, row=1, col=0, title="X: ", width=5, state="readonly")
        self.Y = LabeledEntry(self.frame1, 0, row=1, col=4, title="Y: ", width=5, state="readonly")
        self.Z = LabeledEntry(self.frame1, 0, row=1, col=8, title="Z: ", width=5, state="readonly")
        self.widgets = [self.X, self.Y, self.Z]

class Bob_e_widget(field_impl):
    def __init__(self, frame):
        # To make the graph function only work with the provided button, flag it to not update.
        self.autoUpdate = False

        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)

        self.q = LabeledEntry(self.frame1, .1, row=1, col=0, title="q: ", width=10)
        self.res = LabeledEntry(self.frame1, .1, row=1, col=4, title="res: ", width=10)
        self.widgets = [self.q, self.res]

        """
        # Button to call graphing.
        self.buttonFrame = tk.Frame(frame)
        self.graphButton = tk.Button(self.buttonFrame, text="Graph")
        self.buttonFrame.grid(row=3, column=0)
        self.graphButton.pack()
        """


        self.q.value.trace_add("write", self.trigger_listener)
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
    def __init__(self, master, widget=Fw_widget):
        super().__init__(master, widget)
    
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


    
    def graph(self, plot, fig, lim, *args):
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
    def __init__(self, master, widget=Zero_widget):
        super().__init__(master, widget)
    
    def graph(self, plot, fig, lim, *args):
        plot.axhline(y=0, color='b')

    def GetData(self):
        return {"Zero" : 0}

class bob_e_impl(FieldMethod):
    autoUpdate = False
    def __init__(self, master, widget=Bob_e_widget):
        super().__init__(master, widget)
        # register the graph button to the graphing function

    
    def at(coord, q=1, radius=1, resolution=100, convert=True):
        """
        implementation of the function.
        Inputs:
        """
        #print(f"coord is: {coord}")
        #print(f'FieldMethods_Impl.bob_e_impl.at: bob_e called with charge {q} and radius {radius}')
        # Parameters
        k = 8.8542e-12
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

        thetas = np.linspace(0, np.pi, resolution) # np.array of all the theta values used in the integration (of shape {resolution})
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
                {"q": self.widget.q.value.get(),
                  "res": self.widget.res.value.get()}
                }
    
    def Set(self, key, value):
        if key == "q":
            self.widget.q.value.set(value)
        elif key == "res":
            self.widget.res.value.set(value)

    def graph(self, plot, fig, lim, collection=None, *args):
        """
        When called, will populate the given plot with 
        a contour of the field mags (sum of the zeta, rho components.)
        """
        # Before doing anything, set the axis labels.
        plot.set_xlabel("X-axis")
        plot.set_ylabel("Z-axis")
        plot.set_title("E field mag. on the X-Z plane")

        # Resolution parameters - determines fidelity of graph
        resolution = 100 # determines the number of points created between the bounds
        
        x_l = -3
        x_u = 3

        y_l = -3
        y_u = 3


        ## Construct grid
        x_linspace = np.linspace(x_l, x_u, resolution)
        y_linspace = np.linspace(y_l, y_u, resolution)
        z_linspace = np.zeros(resolution**2)

        gX,gY = np.meshgrid(x_linspace, y_linspace)
        points = np.column_stack(np.vstack([gX.ravel(), z_linspace, gY.ravel()]))

        # For every point, for every coil, orient the point and plug it in the function.
        z_data = self.fx_calc(points, collection)

        sum_Z = np.array(z_data["sum"]).reshape(resolution, resolution)
        smesh = plot.contourf(x_linspace, y_linspace, sum_Z, levels=100,
                                cmap="gist_ncar")
        
        # Colorbar checking
        last_axis_label = fig.axes[-1].get_label() # colorbar is assumed to be the last added axis. So we check the last axis label for existing colorbars.
        #print(fig.axes[-1].get_label())

        # Only create a colorbar if there isn't one detected at the end of the figure.
        if last_axis_label != "<colorbar>":
            cb = fig.colorbar(smesh, ax=plot)

    
    def fx_calc(self, points, coils):
        #print(points)
        sum = []
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._ecalc, point, coils): point for point in points}
            #print(len(futures))
            
            for index, task in enumerate(futures):
                result = task.result()
                #print(result)
                sum.append(result)
        
        return {
            "sum" : sum
        }
    
    def _ecalc(self, point, collection):
        """
        wrapper to orient the point for each coil in the collection, and to call the integration for that point.
        """
        sums = []
        for c in collection.children_all:
            transformed = bob_e_impl.OrientPoint(c, point)
            #print(transformed)
            z, r = bob_e_impl.at(transformed, radius = (c.diameter/2), convert=False)
            #sums.append(z + r)
            sums.append(np.sqrt(z**2 + r**2))
        sums = sum(sums)
        return sums

    
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


        #print(f"started with {point}, ended with {out}")
        return rotated_point
"""
Junk for integrating plotting visuals into the GUI window
"""
import magpylib as mp
from magpylib.current import Circle
from pathlib import Path
import os
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from GuiEntryHelpers import (JSON_to_Df, tryEval)
from GuiHelpers import CSV_to_Df
from BorisAnalysis import CalculateLoss

# etc. graphing funcs
def GraphLoss(figure, vels, bs):
    # return the magnitude of each point's VxB vector
    vcrossmag = CalculateLoss(vels, bs)
    vcrossmag_zero_ind = np.where(vcrossmag==0)
    pass

# CLASS
class TrajGraph(tk.Frame):
    def __init__(self, master, stride_lower=1, stride_upper=100, **kwargs):
        self.master = master
        self.title = "Trajectory"

        #Var to read currently selected Stride
        self.stride_var = tk.IntVar()

        # Instantiate frame
        super().__init__(master, **kwargs)

        # Create slider for Stride
        stride_slider = tk.Scale(self, variable=self.stride_var, 
                                 from_=stride_lower, to=stride_upper,
                                 orient="horizontal")
        stride_label = tk.Label(self, text="Step Stride")
        
        # Create graph
        self.ConstructGraph()

        # Packing
        self.pack(expand=False)
        stride_label.pack()
        stride_slider.pack(anchor="center", fill="x", expand=False)
        self.canvas.get_tk_widget().pack(fill="both", expand=False)
        self.toolbar.pack(side=tk.BOTTOM, fill="x")
    
    def ConstructGraph(self):
            """
            creates a matplotlib figure
            """
            self.fig = plt.figure(figsize=(5,5))
            self.plot = self.fig.add_subplot(1,1,1, projection='3d')

            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.toolbar = NavigationToolbar2Tk(self.canvas, pack_toolbar=False)
            self.toolbar.pack(side="bottom")
            self.canvas.draw()
    
    def File_to_Collection(self, path):
        """
         1. locate the coils file, assuming that path is the dir. to the json.
         2. return the coils as a magpy collection object.
        """
        proot = str(Path(path).parents[0]) # boris_<nsteps>_<simtime>_<nparts>
        #print(f"{path}, {root}")
        coilpath = os.path.join(proot, "coils.txt") # boris_<nsteps>_<simtime>_<nparts>/coils.txt
        print(coilpath)
        df=None
        
        # store coils and rotations separately, so that we can apply the rotations afterwards
        c = mp.Collection()
        df = CSV_to_Df(coilpath, converters={"RotationAngle":tryEval, "RotationAxis":tryEval}, isNum=False, header=0)
        #print(df)
        for i, row in df.iterrows():
            row = row.tolist()
            position = [float(row[0]), float(row[1]), float(row[2])]
            coil = Circle(position, current=float(row[3]), diameter=float(row[4]))

            match row[5]:
                case float():
                    coil.rotate_from_angax(row[5], row[6])
                case int():
                    coil.rotate_from_angax(row[5], row[6])
                case list():
                    out = []
                    for i in range(len(row[5])):
                        coil.rotate_from_angax(row[5][i], row[6][i])
            
            c.add(coil)

        return c


    def UpdateGraph(self, label:tk.Label):
        """
        called whenever the 'plot' button is pressed. Updates the graph in the frame with the trajectory.
        """
        self.plot.cla() # reset plot

        # Read data at the supplied path
        path = label.cget("text")
        c = self.File_to_Collection(path) # magpy.collection object
        df = JSON_to_Df(path) # dataframe

        # Get GUI value for graph resolution
        stride = int(self.stride_var.get())

        # Color scaling based on time
        palettes = ["copper", "gist_heat"]
        nump = df["id"].max() + 1

        # Graph trajectory for each particle
        for part in range(nump):
            # extract data from dataframe
            dfslice = df[df["id"] == part]
            x, y, z = dfslice["px"].to_numpy(), dfslice["py"].to_numpy(), dfslice["pz"].to_numpy() #x, y, z coord points

            print(x)
            # Apply stride by using a bool mask to get every 'stride-th' point.
            mask = np.ones(len(x), dtype=bool)
            mask[:] = False
            mask[np.arange(0, len(x), stride)] = True

            # update the x, y, z arrays with bool mask
            x = x[mask]
            y = y[mask]
            z = z[mask]
            # Color the points based on step count
            colors = mpl.colormaps[palettes[part]]
            self.plot.scatter(x,y,z, cmap=colors, c=np.linspace(0,1,len(x)), s=2.5)

        mp.show(c, canvas=self.plot)
        self.plot.get_legend().remove()
        self.canvas.draw()
        #print(f'graphing finished.')


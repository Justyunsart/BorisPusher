
import numpy as np
import magpylib as magpy
import pandas as pd

from magpy4c1 import EfieldX

from magpylib import Collection

import matplotlib as mpl
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.colors import Normalize
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

from MakeCurrent import current as c
from MakeCurrent import A, B

from math import pi, cos, sin

from BorisAnalysis import CalculateLoss

#=============#
# 3D PLOTTING #
#=============#

def graph_coil_B_cross(c:Collection, lim:int, step:int, fig, root):
    '''
    Helper to visualize the B field of a current in a 2D space (take a cross section).
    The cross section will go from the origin for now

    c = collection of currents from magpylib
    lim = axis boundaries of the graph
    step = the total step count of the graph (higher = more points)
    '''

    # construct grid for the cross section
    x = np.linspace(-lim, lim, step) # these represent LOCAL x and y for the 2D graph, not the 3D space.
    y = np.linspace(-lim, lim, step)

    # calculate B field for the entire grid
    Bs = np.array([[c.getB([i, 0, j]) for i in x] for j in y]) # [bx, by, bz]
    '''
    Bs shape: (step, step, 3)
    '''

    #print(Bs)

    # gather arguments for the streamplot
    X, Z = np.meshgrid(x, y)
    U, V = Bs[:, :, 0], Bs[:, :, 2]

    #print(Bs[71,156])
    #print(c.getB([x[156], 0, y[71]]))
    Bamp = np.sqrt(U**2 + V**2)
    #print(Bamp)
    ind = np.unravel_index(np.argmax(Bamp, axis=None), Bamp.shape)
    print(ind, Bamp[ind], "is at the location: ", x[ind[0]], y[ind[1]])
    #print(U[71][156], V[71][156])

    
    stream = fig.streamplot(X, Z, U, V, color= Bamp, density=1)
    #stream = fig.streamplot(X, Z, U, V, color= Bamp, density=2, norm=colors.LogNorm(vmin = Bamp.min(), vmax = Bamp.max()))
    fig.set_xlabel("X-axis (m)")
    fig.set_ylabel("Z-axis (m)")
    fig.set_title("Magnetic Field Cross Section on the X-Z plane at Y=0")
    root.colorbar(stream.lines)
    

# This is to show that we can get the coil center coordinates from the magpy current's position property. 
# This way, we can create a series of points on the perimeter of the coils to function as point charges for electric field calculations.
def graph_coil_centers():
    points = []
    for current in c.children:
        points.append(current.position) 
    points=np.asarray(points)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=points[:,0],
                               y=points[:,1],
                               z=points[:,2], mode="markers"))

    magpy.show(c, canvas=fig)

    fig.show()
    
# This traces the coil(with diameter=dia) and graphs points around its circumference.
def graph_coil_points(dia, res:int, nsteps:int):
    rad = dia/2
    rads = np.linspace(0, rad, nsteps)
    # need to figure out what axis the slices are
    orientations = []
    points = []
    for current in c.children:
        # Find the direction the circle is facing, for science.
        orientation = current.orientation.as_euler('xyz', degrees=True)
        orientations.append(orientation)

        # Find the interval to plug into the circle formula.
        axis = np.where(orientation > 0) # shows where the circle is facing??
        
        # set local x and y axes (these are indexes of 0 = x, 1 = y, 2 = z)
        if axis[0] == 2:
            xl = 1
            yl = 0
            zl = 2
        elif axis[0] == 0:
            xl = axis[0]
            yl = 2
            zl = 1
        else:
            xl = 1
            yl = 2
            zl = 0

        center = current.position # centerpoint of circle
        #print(center)

        theta = 0
        dtheta = 2*pi/res
        while theta <2*pi:
            p1 = np.array([cos(theta), sin(theta), 0]) # generic circle
            p1arr = np.array(list(map(lambda x: np.multiply(x, p1, dtype=float), rads))).T
            #print(p1arr)
            #p1 = np.multiply(rads, p1).T # circle with the trace's radius

            # adjustments for the local x, y, z vars (based on orientation)
            p2 = np.zeros((3, nsteps))
            p2[xl] = p1arr[0]
            p2[yl] = p1arr[1]
            p2[zl] = p1arr[2]

            p2 = p2.T
            #print(p2.shape)
            p2 += center # move to circle's centers
            points.append(p2)

            theta += dtheta #increment circle angle
    
    points = np.asarray(points)
    #print(points[:,:,0])
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=points[:,:,0].flatten(),
                               y=points[:,:,1].flatten(),
                               z=points[:,:,2].flatten(), mode="markers"))
    magpy.show(c, canvas=fig)
    fig.show()
            
    orientations = np.asarray(orientations)

def graph_trajectory(lim, data):
    '''
    lim = numeric var that depicts the limit value for the chart
    data = the .json output file
    palettes: a list that contains the cmap palettes to use for each particle. 
    '''
    # read the dataframe
    df = pd.read_json(data, orient="table")
    df = df.apply(pd.to_numeric)
    #df = df[df["id"] == 0]

    # create the graph to add to
    fig1 = plt.figure(figsize=(20, 10))
    traj = fig1.add_subplot(2,2,1, projection='3d')
    efig = fig1.add_subplot(2,2,3)
    bfig = fig1.add_subplot(2,2,4)
    #traj = fig1.add_subplot(2,2,1, projection='3d')
    #energy = fig1.add_subplot(2,2,2)
    #energy2 = fig1.add_subplot(2,2,3)
    #energy3 = fig1.add_subplot(2,2,4)
    
    # graphing variables
    palettes = ["copper", "gist_heat"]
    nump = df["id"].max()
    nums = int(df.shape[0] / (nump + 1))
    stride = 1 # controls resolution of graphed points

    for part in range(1):
        # extract data from dataframe
        dfslice = df[df["id"] == 0]
        x, y, z = dfslice["px"].to_numpy(), dfslice["py"].to_numpy(), dfslice["pz"].to_numpy()
        v = np.c_[dfslice["vx"].to_numpy(), dfslice["vy"].to_numpy(), dfslice["vz"].to_numpy()]
        b = np.c_[dfslice["bx"].to_numpy(), dfslice["by"].to_numpy(), dfslice["bz"].to_numpy()]

       #vdotv = list(map(lambda x: np.dot(x, x), v))
        #bdotb = list(map(lambda x: np.dot(x, x), b))

        print(v.shape)

        # loss logic
        #vcrossmag, vcrossmagD1, vcrossmagD2 = CalculateLoss(vels=v, bs=b)


        # trajectory logic
        # boolean mask to decrease density of plotted points
        mask = np.ones(len(x), dtype=bool)
        mask[:] = False
        mask[np.arange(0, len(x), stride)] = True

        # update the x, y, z arrays with bool mask
        x = x[mask]
        y = y[mask]
        z = z[mask]
        #z *= 0

        colors = mpl.colormaps[palettes[part]]

        # connecting lines
        segments=np.stack((np.c_[x[:-1], x[1:]], np.c_[y[:-1], y[1:]], np.c_[z[:-1], z[1:]]), axis=2)
        #print(segments)
        segmentcolors= colors(np.linspace(0,1,len(segments)))
        lines = Line3DCollection(segments, linewidths=1, zorder=1, colors=segmentcolors) 

        # plot everything
        traj.scatter(x,y,z, cmap=colors, c=np.linspace(0,1,len(x)), s=2.5)
        graph_E_X(3, 100, efig)
        graph_coil_B_cross(c, 3, 100, bfig, fig1)
        #traj.add_collection(lines)

        #energy.plot(vcrossmag[:-1])
        #energy2.plot(vcrossmagD1[:-1])
        #energy3.plot(vcrossmagD2[:-1])

        
    # Set 3D plot bounds
    #traj.set_xlim3d(-lim,lim)
    #traj.set_ylim3d(-lim,lim)
    #traj.set_zlim3d(-lim,lim)
    
    # Extract the positional data from the dataframe
    #x, y, z = df["px"].to_numpy(), df["py"].to_numpy(), df["pz"].to_numpy()
    
    # Get the smallest index of when to stop graphing
    # This feels kinda ugly I'm not going to lie.
    #xs = np.asarray((x>lim) | (y > lim) | (z > lim)).nonzero()

    #if(len(xs[0]) != 0):
    #     ind = xs[0][0] 
    #else: 
    #    ind = -1
    
    # Plot it to the index
    #traj.plot(x, y, z)
    magpy.show(c, canvas=traj)

    # Enjoy the fruits of your labor
    plt.show()

def graph_E_X(lim:int, step:int, subplot):

    # construct grid for the cross section
    x = np.linspace(-lim, lim, step) # these represent LOCAL x and y for the 2D graph, not the 3D space.

    E = np.multiply(A * np.exp(-(x / B)** 4), (x/B)**15)

    subplot.plot(x,E)

def graph_coil_B():
    fig = plt.figure()

    f1 = fig.add_subplot(121, projection="3d")
    f2 = fig.add_subplot(122, aspect="equal")

    magpy.show(c, canvas=f1, row=1, col=1)
    graph_coil_B_cross(c, 3, 100, f2, fig)

    plt.show()


#root = str(Path(__file__).resolve().parents[1])
#outd = root + "/Outputs/boris_500000_20.0_2_(13)/dataframe.json"

#df = pd.read_json(outd, orient="table")
#df = df.apply(pd.to_numeric)
#print(df)

# graph_trajectory(500, df)
#graph_coil_centers()
#graph_coil_points(dia = 500, res = 100, nsteps=100)
#graph_coil_B_cross(c=c, lim=3, step=200)
#print(c.getB((0,0,0)))
#print(c.getB((-2,0,2)))
#graph_coil_B()

#if __name__ == "__main__":
    #graph_coil_B()

'''
def make_vf_3d_boris(x_lim, y_lim, z_lim, num_points):
    global path
    #------------------------#
    # set visuals for figure #
    #------------------------#
    fig2 = plt.figure(figsize=(10, 20))
    
    # 3d projection
    ax1 = fig2.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig2.add_subplot(1, 2, 2)

    # setting up grid for plot
    ax1.set_xlim3d(x_lim)
    ax1.set_xlim3d(y_lim)
    ax1.set_zlim3d(z_lim)

    lineSens = magpy.Sensor()
    lineSens.move(np.linspace((x_lim[0], 0, 0), (x_lim[1], 0, 0), 1000), start=0)

    # setting x,y,z from the travel points


    # setting colors for the magnitude at each point used
    #setting up colors
    colRes = []
    for col in range(len(x)):
        colRes.append(col)
    norm = Normalize()
    norm.autoscale(colRes)
    colormap = cm.inferno

    for point in range(0,num_points,2000):
        if not (x[point] > x_lim[1]) and not (x[point] < x_lim[0]) and not (y[point] > y_lim[1]) and not (y[point] < y_lim[0]) and not (z[point] > z_lim[1]) and not (z[point] < z_lim[0]) and not (x[point] == 0.0):
            ax1.plot(x[point:point+2001:1],
            y[point:point+2001:1],
            z[point:point+2001:1],
            color=colormap(norm(colRes[point])))
            if point % 10000 == 0:
                print("point plotted " + str(point))
        else:
            print("Exited Early")
            break
    lim = 2400

    # Energy calc on beginning and end velocities

    velS = B[0][0] ** 2 + B[0][1] ** 2 + B[0][2] ** 2
    velE = B[-1][0] ** 2 + B[-1][1] ** 2 + B[-1][2] ** 2
    vDiv = abs(velS-velE)/((velS+velE)/2)*100

    # magnetic moment
    # Bf = np.squeeze(np.where((A[:, 0] < 0.21) & (A[:, 0] > -0.21)))  # used for finding index of closest values to x==0

    Bf = np.asarray(B[:-1, 0]*B[1:, 0] < 0).nonzero()[0]  # used for finding index of bounce points
    # print(Bf)


    BfS = Bf[0]
    BfE = Bf[-1]
    BfMag = []
    BfVel = []
    MagMoment = []

    # getting a list of B magnitudes and perpendicular velocity for bounce points
    for x1 in range(len(Bf)):
        BfMag1 = (math.sqrt(B0List[x1][0] ** 2 +
                            B0List[x1][1] ** 2 +
                            B0List[x1][2] ** 2)) / 1000
        BfVel1 = B[x1][1] ** 2 + B[x1][2] ** 2
        MagMoment1 = BfVel1 / BfMag1

        BfMag.append(BfMag1)
        BfVel.append(BfVel1)
        MagMoment.append(MagMoment1)

    # first and last bounce point magnitudes
    BfSmag = BfMag[0]
    BfEmag = BfMag[-1]
    magMomentS = MagMoment[0]
    magMomentE = MagMoment[-1]
    bDiv = abs(magMomentS - magMomentE) / ((magMomentS + magMomentE) / 2) * 100
    print("List of points at x ~ 0: {}".format(Bf))
    print("BfS parameters: {}, BfE parameters: {}".format(A[BfS], A[BfE]))
    print("mag begin : " + str(BfSmag))
    print("mag end : " + str(BfEmag))

    # Ticker = M ticks, set the axis locator
    # trajectory graph
    M = 5
    ticks = ticker.MaxNLocator(M)
    ax1.xaxis.set_major_locator(ticks), ax1.yaxis.set_major_locator(ticks), ax1.zaxis.set_major_locator(ticks)
    ax1.set_xlim([-lim, lim]), ax1.set_ylim([-lim, lim]), ax1.set_zlim([-lim, lim])
    ax1.set_xlabel('x'), ax1.set_ylabel('y'), ax1.set_zlabel('z')  # label axes
    '''
'''
    ax1.set_title("Start point: Xx={:.5e},Xy={:.5e}, Xz={:.5e} \n "
                    "Start Velocity: Vx={:.5e}, Vy={:.5e}, Vz={:.5e} \n "
                    "End Velocity : Vx={:.5e}, Vy={:.5e}, Vz={:.5e} \n "
                    "V^2 Start: {:.5e}, End: {:.5e}, Loss%: {:.5e} \n "
                    "Magnetic Moment Start: {:.5e}, End: {:.5e}, Loss%: {:.5e} ".format
                    (Df.iloc[0], Df.iloc[1], Df.iloc[2],
                    Df.iloc[3], Df.iloc[4], Df.iloc[5],
                    B[-1][0], B[-1][1], B[-1][2],
                    velS, velE, vDiv,
                    magMomentS, magMomentE, bDiv))
    '''
'''
    cbar = fig2.colorbar(cm.ScalarMappable(norm=norm, cmap=colormap), ax=ax1, fraction=0.040, pad=0.04)
    cbar.ax.set_ylabel("Timestep (out of " + str(ft) + " seconds)")

    # line graph
    keys = gradList.keys()
    values = gradList.values()
    gradAdd = 0.0
    for thing in keys:
        gradAdd += (gradList[thing])
    gradSpace = np.linspace(0, gradAdd, ending)
    ax2.plot(BfVel)
    # ax2.plot(gradSpace, accelList)
    # ax2.set_title("dt = V/A")
    # ax2.set_ylabel("delta t")
    # ax2.set_xlabel("num points")

    # bar graph
    # ax3.bar(keys, values)
    # ax3.set_title('Delta t ratio')

    # trajectory plot
    # ax4.scatter(x, y, z, s=0.1)
    # ax4.set_title('Coil Array\n Total Velocity={:.2e}'.format(math.sqrt(VelX**2 + VelY**2 + VelZ**2)))

    # converting x,y,z points into 2D list
    cut = int(num_points/1000)
    sensArray = np.column_stack((x, y, z))
    sensArrayCut = sensArray[0::cut]
    # creating Sensor for particle
    partSens = magpy.Sensor(pixel=[(0, 0, 0)], style_size=1)
    partSens.position = sensArrayCut
    # setting the coils into the plot
    # magpy.show(c, canvas=ax1)
    with magpy.show_context(c, animation=True, backend='plotly', opacity=0.5):
        magpy.show(partSens, col=1)
        # magpy.show(lineSens, output='B', col=2, pixel_agg=None)
        magpy.show(partSens, output='B', col=2, pixel_agg=None)
    plt.show(block=True)
    plt.close()

    # fig3 = plt.figure(figsize=(10, 10))
    # ax = fig3.add_subplot(projection='3d')
    # ax.scatter(x,y,z, s=0.01)
    # plt.show(block=True)
    # plt.close()
    '''
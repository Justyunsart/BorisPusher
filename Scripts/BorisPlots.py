import os

import numpy as np
import magpylib as magpy
import pandas as pd

from magpylib import Collection

import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.colors import Normalize
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

from MakeCurrent import current as c
from pathlib import Path
from scipy.spatial.transform import Rotation

from sympy import solve, Eq, symbols, Float


#=============#
# 3D PLOTTING #
#=============#


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
def graph_coil_points(dia, res:int):
    rad = dia/2
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

        span = np.linspace(center[xl] - rad, center[xl] + rad, res) # evenly spaced intervals on the circle's major axis to create the points.
        for s in span:
            y = symbols('y')
            eq1 = Eq((Float(s) - Float(center[xl]))**2 + (y - Float(center[yl]))**2, rad**2)
            sol = solve(eq1) # this will give us all the local y axis values for the circle.

            for j in sol:
                # trace the circle with the points we just found
                point = np.zeros(3, dtype=float)
                point[xl] = s
                point[yl] = j
                point[zl] = center[zl]

                # rotate!!! for more! points!
                point1 = np.zeros(3, dtype=float)
                point1[xl] = j
                point1[yl] = s
                point1[zl] = center[zl]

                points.append(point)
                points.append(point1)
    
    points = np.asarray(points)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=points[:,0],
                               y=points[:,1],
                               z=points[:,2], mode="markers"))
    magpy.show(c, canvas=fig)
    fig.show()
            


    orientations = np.asarray(orientations)

    # span = np.linspace()

def graph_trajectory(lim, data):
    # create the graph to add to
    fig1 = plt.figure(figsize=(10, 20))
    traj = fig1.add_subplot(1,1,1, projection='3d')

    # Set 3D plot bounds
    traj.set_xlim3d(-lim,lim)
    traj.set_ylim3d(-lim,lim)
    traj.set_zlim3d(-lim,lim)
    
    # Extract the positional data from the dataframe
    x, y, z = data["px"].to_numpy(), data["py"].to_numpy(), data["pz"].to_numpy()

    # Get the smallest index of when to stop graphing
    # This feels kinda ugly I'm not going to lie.
    xs = np.asarray((x>lim) | (y > lim) | (z > lim)).nonzero()

    if(len(xs[0]) != 0):
         ind = xs[0][0] 
    else: 
        ind = -1
    
    # Plot it to the index
    traj.plot(x[:ind], y[:ind], z[:ind])
    magpy.show(c, canvas=traj)

    # Enjoy the fruits of your labor
    plt.show()


root = str(Path(__file__).resolve().parents[1])
outd = root + "/Outputs/boris_500000_20.0_2_(13)/dataframe.json"

df = pd.read_json(outd, orient="table")
df = df.apply(pd.to_numeric)
#print(df)

# graph_trajectory(500, df)
# graph_coil_centers()
# graph_coil_points(dia = 500, res = 10)

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
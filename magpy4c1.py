import math
import time
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import magpylib as magpy
import os

# used to create output restart file
import pandas as pd

# gui stuff
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

# magpy and plots
from magpylib.current import Loop
from magpylib import Collection
from matplotlib import ticker
from matplotlib.colors import Normalize
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

pd.set_option('display.max_columns', None)
#######
# GUI #
#######
'''
Testing the code by changing parameters and numsteps and everything became too cumbersone, so I decided to
bite the bullet and create some GUI for it. 
'''

# Application Window
root = Tk()
root.title("Configure Sim")

# Content Frame
#    > Holds contents of the UI
mainframe = ttk.Frame(root, padding = "3 3 12 12")
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

rframe = ttk.Frame(root, padding = "3 3 12 12")
rframe.grid(column=1, row=0, sticky = (N, W, E, S))

#=============#
# GUI WIDGETS #
#=============#
# HELPERS

'''
File explorer for restart files
'''

# Variable to store the dir of the input file
inpd = ""
def browseFiles():
    filename = filedialog.askopenfilename(title = "Select a Restart File")
    button_restart_file.configure(text = filename)
    inpd = filename

'''
Display Timestep Widget
'''
def CalcTimestep(time, numsteps):
    ## Display Calculated Timestep
    v = (time.get()) / (numsteps.get())
    return v

'''
Update Timestep value and label in the GUI when numsteps/sim time are updated
'''
def DTcallback():
    global time_step_value
    val = CalcTimestep(entry_sim_time_value, entry_numsteps_value)
    time_step_value = val
    label_time_step.configure(text = "Timestep: " + str(val))
    return True

'''
Toggles
'''
def FileCallback():
    if(do_file.get() == False):
        # print("button disabled")
        button_restart_file.configure(state = "disabled")
        return True
    else:
        # print("button enabled")
        button_restart_file.configure(state = "enabled")
        return True

# WIDGETS
## Display terminal output?
doDisplay = BooleanVar(value = True)
checkDisplay = ttk.Checkbutton(mainframe,
                               text = "Crap in Terminal?",
                               variable = doDisplay,
                               onvalue = True,
                               offvalue = False)

## Read restart file?
do_file = BooleanVar(value = False)
check_restart_file = ttk.Checkbutton(mainframe,
                                     variable = do_file,
                                     text = "Read Input File?",
                                     onvalue = True,
                                     offvalue = False,
                                     command = FileCallback)


label_restart_file = ttk.Label(mainframe,
                               text = "Restart File Dir:").grid(column = 0, row = 1, sticky=(W))
button_restart_file = ttk.Button(mainframe,
                                 text = "Browse Files",
                                 command = browseFiles)
button_restart_file.grid(column = 1, row = 1)

### Make sure the button is in the correct state to start
FileCallback()

## Numsteps
label_numsteps = ttk.Label(mainframe,
                           text = "Number of Steps: ").grid(column = 0, row = 3)

entry_numsteps_value = IntVar(value = 500000)
entry_numsteps = ttk.Entry(mainframe,
                           textvariable = entry_numsteps_value,
                           validate = "focusout",
                           validatecommand = DTcallback)
entry_numsteps.grid(column = 1, row = 3)

## Total Time to Simulate - Simulation Time
label_sim_time = ttk.Label(mainframe,
                           text = "Sim Time: ").grid(column = 0, row = 4)
entry_sim_time_value = DoubleVar(value = 20.0)
entry_sim_time = ttk.Entry(mainframe,
                           textvariable = entry_sim_time_value,
                           validate = "focusout",
                           validatecommand = DTcallback).grid(column = 1, row = 4)

## Display Calculated Timestep
time_step_value = (entry_sim_time_value.get()) / (entry_numsteps_value.get())
label_time_step = ttk.Label(rframe,
                            text = "Time step: " + str(time_step_value))
## Caclulate button
button_calculate = ttk.Button(mainframe,
                              text = "Calculate",
                              command = root.destroy) # Close the window so the rest of the program can run

# Display the widgets
for w in mainframe.winfo_children():
    w.grid_configure(padx = 5, pady = 5)
for w in rframe.winfo_children():
    w.grid_configure(padx=5,pady=5)

# Run GUI loop
root.mainloop()

###################
# INPUT FILE JUNK #
###################
#======#
# VARS #
#======#
simDf = pd.DataFrame(columns=["pind", "step", "position", "velocity", "acceleration"])
simDict = {}

initialized = False # Ensure initialization only happens once : failsafe
cwd = os.getcwd() # Gets the current working directory, so we can find the Inputs, Outputs folder easily.
outd = cwd + "/Outputs" 

psensors = magpy.Collection()
#=================================#
# HELPERS FOR READING INPUT FILES #
#=================================#
def StrToArr(text):
    return np.fromstring(text, sep = ' ')

'''
From the GUI: 
1. Determine if we're reading input data or not.
2. Populate the dataframe accordingly.

For each dataframe row:
1. Create a Particle object
2. Apply the data from the input file to its fields
3. Store the Particle object in an array

Magpy integration:
1. Create a magpy.collection of magpy.sensors corresponding to each particle
    > The index of each sensor will correspond to the index of the particle

IMPORTANT:
    > Whether we read input data or not comes from the 'do_file' var from the GUI.
    > The dataframe is a table of Particle classes.
        - row # = particle index
        - column = attribute
    > 'inpd' is set whenever the input file dir is updated, to the file's dir.
'''

def InitializeData():
    global initialized
    global simDf
    # Making sure initialization only happens once
    assert initialized == False
    initialized = True

    if(do_file.get() == False):
        data = pd.read_csv(cwd + "/Inputs/Default_Input.txt", dtype = {"positions" : str, "vels" : str, "accels" : str})
    else:
        data = pd.read_csv(inpd, dtype = {"positions" : str, "vels" : str, "accels" : str})
    
    # CLEANING

    # Convert columns to Arrays
    data["starting_pos"] = data["starting_pos"].str.split(" ").apply(pd.to_numeric, errors = "coerce")
    data["starting_vel"] = data["starting_vel"].str.split(" ").apply(pd.to_numeric, errors = "coerce")
    data["positions"] = data['positions'].str.split(" ").apply(pd.to_numeric, errors = "coerce")
    data["vels"] = data["vels"].str.split(" ").apply(pd.to_numeric, errors = "coerce")
    data["accels"] = data["accels"].str.split(" ").apply(pd.to_numeric, errors = "coerce")

    # print(data["starting_pos"])

    # Create sensors
    i = 0
    for r in data.to_numpy():
        print("creating sensor for ", r)
        sensor = magpy.Sensor(position = r[0])
        psensors.add(sensor)

        simDict[i] = [0, r[0], r[1]]
        i += 1

    return data

'''
Functions access it directly
'''
df = InitializeData() # Populate this ASAP lol

'''
Prints out the resulting dataframe from the InitializeData() to debug
'''
def TestInitialization():  
    print(f"Dataframe: {df}")
    print(f"simDict: {simDict}")
    print(f"Sensors: {psensors.children}")

'''
Creates the output file
'''
def CreateOutput(df):
    global outd
    print(df)
    df.to_csv(outd + "/out3.txt", index = False)


## Uncomment below to check if the dataframe is being set properly.
TestInitialization()

# creates a square box of Loop coils
def Circle(a, dia, d, gap):
    # current Loop creation, superimpose Loops and their fields
    s1 = Loop(current=a, diameter=dia).move([-(d/2)-gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s2 = Loop(current=-a, diameter=dia).move([(d/2)+gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s3 = Loop(current=-a, diameter=dia).move([0,-(d/2)-gap,0]).rotate_from_angax(90, [1, 0, 0])
    s4 = Loop(current=a, diameter=dia).move([0,(d/2)+gap,0]).rotate_from_angax(90, [1, 0, 0])
    s5 = Loop(current=a, diameter=dia).move([0,0,-(d/2)-gap]).rotate_from_angax(90, [0, 0, 1])
    s6 = Loop(current=-a, diameter=dia).move([0,0,(d/2)+gap]).rotate_from_angax(90, [0, 0, 1])

    c = Collection(s1,s2,s3,s4,s5,s6, style_color='black')
    return c


# helmholtz setup for a test
def Helmholtz(a, dia, d):
    # helmholtz test
    s7 = Loop(current=a, diameter=dia).move([-(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])
    s8 = Loop(current=a, diameter=dia).move([(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])

    c = Collection (s7, s8)
    return c

#=========#
# B FIELD #
#=========#
'''
TODO:
- Make this work on an entire nested array instead of one array at a time.
- Possible multithreading?
Input: Array of (nparticle x pos(3)) dim
Output: Array of (nparticle x bf(3)) dim

Ensure the code is efficient because the whole point of these operations is to increase computational speed
'''

# using magpylib, this calculates the b-field affecting the particle
# unless it is outside of the bounds given by 'side'
def Bfield(y):
    global side
    # Create out array
    out = np.empty(len(y), dtype= np.ndarray)

    # Update sensor positions
    for p in range(len(y)):
        pos = y[p]
        isBounds = pos.any() > side
        Bf = [0., 0., 0.]

        if(not isBounds):
            sens = psensors.sensors[p]
            sens.position = pos
            Bf = c.getB(sens, squeeze=True)

        out[p] = Bf
    
    return Bf


    # base statement set for stopping calculations outside of the given area


    # returning the b-field at the given point, or [0,0,0] if outside of the given area
    return f

# global variables
magpy.graphics.style.CurrentStyle(arrow=None)
accel = None

# physics variables
a = 1.0e5 # current
aa = a / 1.72 # triangle current
dia = 500. # coil diameter
d = 800. # coil placement
l = 600 # line space(x, y, z variables)
r = 100 # line space increments
VelX = 5.8e5 # velocity in the 'X' direction for the particle In mm/s
VelY = VelX # velocity in the 'Y' direction for the particle In mm/s
VelZ = 0.0 # velocity in the 'Z' direction for the particle In mm/s
t1 = -10.
t2 = -10.

######################
# DEFAULT PARAMETERS #
######################
'''
If some elements in the GUI are not populated, the sim will use these conditions.
'''

# the initial starting point and velocity vectors in a list
yNot = np.array([[0., 0., 120., VelX/1.5, VelY, VelZ],
                 [0., 0.,-120., -VelX, VelY/1.5, VelZ],
                 [0., 0., 0., -VelX, -VelY, VelZ],
                 [0., 0., 0., -VelX, VelY, -VelZ],
                 [0., 0., 0., VelX, -VelY, -VelZ],
                 [0., 0., 0., -VelX, -VelY, -VelZ]])

# E = np.array([0.0, 0.0, 0.0])  # Volts/m
# B = [18000, 0, 0]
s,t = 450,30

# plotting variables
step = 50 # vector density
smLine = 1
edge = 125 # sets square coil length
limS = 600 # vector graph area
print(limS)

# setting limit space to cancel calculations outside of it
x_lim = (-limS, limS)
y_lim = (-limS, limS)
z_lim = (-limS, limS)
radi = 200
plot_pick = None
#num_points = 3500000

corner = 1 # sets octagonal corner size (cannot be 0)
side = limS # max range for plot
gap = 15 # sets space between coils
coilLength = 1000
# dt = coilLength / (math.sqrt(VelX**2 + VelY**2 + VelZ**2) * num_points)
dt = time_step_value
print(dt)

# comment in coils array you wish to use from the above definitions
# c = Helmholtz(a, dia, d)
c = Circle(a, dia, d, gap)

print(c.getB([450, 0, 0]))


# boris push calculation
# this is used to move the particle in a way that simulates movement from a magnetic field
# mass and charge are set to 1, and input as 'm' and 'q' respectively
def borisPush(q, m, num_points, B0List, dt, accelList, gradList):
    global side
    global df

    # print(f"Dataframe inside Boris: {df}")
    mass = m
    charge = q
    vAc = 1
    mm = 0.001
    # mm = 0.01 in velocity conversion line 148 results in Global Garbage.
    ft = 0

    duration = num_points
    # duration = int(time)
    # assumes parameter for velocity was in mm/s, converts it to m/s

    v = df["starting_vel"].to_numpy() * mm
    x = df["starting_pos"].to_numpy() * mm

    v = v[0]
    print(f"v has a len of {len(v)}")
    print(v, x)
    print(x[0])

    E = np.array([0., 0., 0.])

    # X = np.zeros((duration, 3))
    # V = np.zeros((duration, 3))

    dTimer = 0
    for time in range(duration):
        Bf = Bfield(x)
        B0List.append(Bf)
        # print("bf: ", Bf)

        tt = charge / mass * Bf * 0.5 * dt
        ss = 2. * tt / (1. + tt * tt)
        v_minus = v + charge / (mass * vAc) * E * 0.5 * dt
        v_prime = v_minus + np.cross(v_minus, tt)
        v_plus = v_minus + np.cross(v_prime, ss)
        v = v_plus + charge / (mass * vAc) * E * 0.5 * dt

        x[0] += v * dt

        # creating a gradient of resolution based on the acceleration and velocity for dt
        vel = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        # print(f"velocity: {vel}")
        accelVec = (v_plus - v_minus) / dt
        accel = math.sqrt(accelVec[0]**2 + accelVec[1]**2 + accelVec[2]**2)
        '''
        if not accel == 0:
            if (vel/accel)/1e3 < dt:
                dt = (vel / accel) / 1e3
                gradList['V/A'] += 1
            else:
                dt = (coilLength / vel) / 1e3
                gradList['L/V'] += 1
        else:
            dt = (coilLength / vel) / 1e3
            gradList['L/V'] += 1
            '''
        print(x[0])
        accelList = np.append(accelList, [[accelVec[0], accelVec[1], accelVec[2], accel]], axis=0)
        # X[time, :] = x
        df["positions"] = np.append([df["positions"]], [x[0]]) # positions array
        # V[time, :] = v
        df["vels"] = np.append([df["vels"]], [x[0]]) # velocity array
        df["accels"] = np.append([df["accels"]],[[accelVec]]) # acceleration array
        # print(row)

        dTimer += 1
        ft += dt # total time spent simulating
        if dTimer % 1000 == 0:
            print("boris calc * " + str(dTimer))
            print("total time: ", ft, dt)
        if x[0][0] > side or x[0][1] > side or x[0][2] > side:
            print('Exited Boris Push Early')
            break
    print(ft*(10**-5))
    ft = ft*(10**-5)
    return dTimer, ft, accelList

#=============#
# 3D PLOTTING #
#=============#
def make_vf_3d_boris(x_lim, y_lim, z_lim, num_points):
    global path
    global df
    #print(y0)
    B0List = []
    accelList = np.zeros((1,4))
    # gradList = {'1e8': 0, '8e7': 0, '5e7': 0, '1e7': 0, '5e6': 0, '1e6': 0, '5e5': 0}
    gradList = {'V/A': 0, 'L/V': 0}
    q = 1.602e-19
    m = 1.67e-27

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

    print("plotting done")
    if part_val == 'y':
        # testing the boris push method for particle movement

        ending, ft, accelList = borisPush(q, m, num_points, B0List, dt, accelList, gradList)
        print(f"Dataframe: {df}")
        A = df.get("positions")
        B = df.get("vels")
        print(f"positions: {A}")
        print(f"velocities: {B}")

        # setting x,y,z from the travel points
        x, y, z = [i[0] for i in A], \
                    [i[1] for i in A], \
                    [i[2] for i in A]

        # setting colors for the magnitude at each point used
        #setting up colors
        colRes = []
        for col in range(len(x)):
            colRes.append(col)
        norm = Normalize()
        norm.autoscale(colRes)
        colormap = cm.inferno

        # plotting the 3d path of the particle
        # removing 0's to show a better visual
        # x = [float('nan') if h == 0 else h for h in x]
        # y = [float('nan') if h == 0 else h for h in y]
        # z = [float('nan') if h == 0 else h for h in z]
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
        print(Bf)


        BfS = Bf[0]
        BfE = Bf[-1]
        BfMag = []
        BfVel = []
        MagMoment = []

        # getting a list of B magnitudes and perpendicular velocity for bounce points
        for x1 in Bf:
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
        ax1.set_title("Start point: Xx={:.5e},Xy={:.5e}, Xz={:.5e} \n "
                      "Start Velocity: Vx={:.5e}, Vy={:.5e}, Vz={:.5e} \n "
                      "End Velocity : Vx={:.5e}, Vy={:.5e}, Vz={:.5e} \n "
                      "V^2 Start: {:.5e}, End: {:.5e}, Loss%: {:.5e} \n "
                      "Magnetic Moment Start: {:.5e}, End: {:.5e}, Loss%: {:.5e} ".format
                      (df.iloc[0], df.iloc[1], df.iloc[2],
                       df.iloc[3], df.iloc[4], df.iloc[5],
                       B[-1][0], B[-1][1], B[-1][2],
                       velS, velE, vDiv,
                       magMomentS, magMomentE, bDiv))
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


x_val = "n"
y_val = "n"
z_val = "n"
# asking if the user wants to calculate particle confinement
# part_val = input("Calculate particle confinement y/n: ")
part_val = input("calculate particles? y/n: ")

make_vf_3d_boris(x_lim, y_lim, z_lim, entry_numsteps_value.get())

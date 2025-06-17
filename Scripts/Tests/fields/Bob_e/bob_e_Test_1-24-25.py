"""
Test implementation of Bob's e field
Before putting it in the program implementation.

"""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colors

# multithreading
import concurrent.futures

class coil():
    '''
    coil: a class that holds metadata for coils. Expected to be circular.
    
    Properties:
    radius: the radius of the coil.
    position: the location of the center of the circle in cartesian space.
    axis: a description of the plane the cirlce is aligned with.
        - a string with two of tree axes (eg. 'XY').
    '''
    
    ## Radius
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, value):
        self._radius = value

    ## Position
    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = value

    ## Rotation
    """
    Axis property (default='XY'):
         - describes the plane of the circle (two of XYZ)
    """
    @property
    def axis(self):
        return self._axis
    @axis.setter
    def axis(self, value):
        self._axis = value

    def __init__(self, radius=1, x=0, y=0, z=0, axis='XY'):
        # Set properties to given or default values
        self.radius = radius
        self.position = [x,y,z]
        self.axis = axis

def toCyl(coord):
    """
    toCyl: a helper function.
        - Takes in an input coordinate in cartesian space
        - Outputs its equivalent in cylindrical space.
    """
    rho = np.sqrt(coord[0]**2 + coord[1]**2)
    azimuth = np.arctan2(coord[1], coord[0])
    return np.array([rho, azimuth, coord[2]])

def bob_e(coord, radius=1, convert=True):
    """
    bob_e: Implementation of Bob's E field integrals.

    Inputs:
    coord: The coordinate in either cartesian or cylindrical space to calculate the E field at.
    radius: The radius of the coil, defaults to 1.
    convert: Bool (defaults to True) that flags the system to convert the input coordinate to cyl space.
        - By default, the function assumes a cartesian input.

    Outputs:
    zeta, rho: The Ezeta and Erho components of the E field.
    r1: The input point's rho component (used for graphics)
    """
    #print(f"point: {coord}")

    # Parameters
    q = 1 # charge 
    k = 8.8542e-12
    kq_a2 = (k * q)/(radius**2)

    resolution = 1000 # the amount of intervals from 0 to pi

    # Coordinate Constants
    if convert:
        coord = toCyl(coord)
        #print(f"rotated: {coord}")
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
    
    fzeta = 1/denominators
    frho = (1 - cosines / rho) / denominators

    '''
    for i in range(resolution + 1): # one is added here so that the last step will be pi.
        theta = i * (np.pi/resolution) # theta slice

        denominator = (1 - ((2 * rho * np.cos(theta))/mag)) ** (3/2) # shared denominator for frho, fzeta integration.
        
        fzeta.append(1/denominator)

        if (rho != 0): # protection for 0 edge case.
            frho.append((1 - np.cos(theta)/rho)/denominator)
        else:
            frho.append(0)
    '''
    
    # Final - fzeta, frho is summed, multiplied by the integration constant and kq.a^2.
    zeta = np.asarray(fzeta).sum() * Fzeta_c * kq_a2
    rho = np.asarray(frho).sum() * Frho_c * kq_a2
    #zeta = np.asarray(fzeta).sum() * Fzeta_c
    #rho = np.asarray(frho).sum() * Frho_c
    return zeta, rho, r1

def testPoints(zeta_goal, range_u, range_l, resolution, theta = 1, radius=1):
    """
    testPoints: a helper function to generate input coordinates in cyl space, following a desired zeta value (zeta = z/radius)

    takes in an input of a desired zeta value, range, and resolution.
    returns a grid of points.
    """
    z = np.ones(resolution) * (radius * zeta_goal)
    #print(z)
    azimuth = np.ones(resolution) * theta
    #print(azimuth)
    rhos = np.linspace(range_l, range_u, resolution)
    #print(rhos)
    return np.column_stack((rhos, azimuth, z))

# graphics parameters
grid_zetas = [0.002, 0.1, 0.5, 1, 2, 3]
data = {}

def GenerateGrid(lower, upper, resolution, zetas):
    """
    GenerateGrid: a helper function that calls testPoints for each given zeta value, effectively providing a list of cyl coordinate inputs to plug in.

    Inputs:
        lower, upper: the x-axis bounds of the grid
        resolution: the number of points to generate between the two bounds
        zetas: a list containing all the desired zeta values.

    Data:
        The function doesn't explicitly output anything, but it edits the global data variable.
        'data' is a dictionary in which all the keys are strings 'zeta = <zeta value>', and the values are a list of all the input points.
    """
    global data

    for zeta_desired in zetas:
        grid = testPoints(zeta_desired, range_u=upper, range_l=lower, resolution=resolution)
        label = f"zeta = {zeta_desired}"

        data[label] = grid # add entry to data dict

def fzeta_plug(out, world=True):
    """
    fzeta_plug: a helper function used in graphics. Plugs in points from the data dictionary and stores the fzeta value into the output folder

    Inputs:
        out: the output folder to store fzeta
        world: a bool value (default = True) to indicate whether the out points should be in world space.
    """
    global data
    vals = list(data.values())

    for i in range(len(vals)):
        out.append([])
        for point in vals[i]:
            z, r, r1 = bob_e(point, convert=False)
            if world:
                out[i].append([point[0], z])

def coil2origin(point:np.ndarray, axis):
    """
    coil2origin: a helper function for transformations. Rotates the input point in 3D space so that its corresponding coil is on the YX plane.
        - Rotation is done with matrix multiplication of 90 degree rot matrices in the corresponding axis, depending on the input axis.
        - only the "YZ" plane is implemented because we currently only are looking at vertical coils.

    Inputs:
        point: the cartesian coordinates of the input point
        axis: a string that respresents the coil's currently aligned plane (a property of the coil class)

    """
    match axis:
        case "YZ":
            """
            The coil is facing the YZ plane.
            This means that going to the XY plane needs 90 in the Y axis.
            """
            mat = np.array([[0,0,1], [0,1,0], [-1,0,0]])
            out = np.matmul(mat, point)
            #print(f"{point} rotated 90 degrees is: {out}")
            return out 
        case "XY":
            """
            The coil is already in the XY plane,
            So that no rotations need to be done.
            """
            return point


def coilTransformation(in_c, center_c):
    """
    Inputs:
    in_c: the cartesian coordinates of the point to calculate E at.
    center_c: the cartesian coordinate of the coil center
    """
    ## Step 1a: get connecting vector between input and center coordinates
    cv = in_c - center_c
    ## Step 1b: dot the connecting vector with normal axes to get alpha, beta, gamma
    abg = np.dot(cv, [[1,0,0], [0,1,0], [0,0,1]])
    point = in_c * abg

    print(f'abg: {abg}')





def calc_E(grid:list, coils:list):
    """
    calls the bob_e function with transformed coordinates, then transforms everything back to world coordinates

    parameters:
    grid: a container of input points in cartesian space. 
    coils: a container with all the coil objects involved.
    """

    ## For every coil involved, first transform everything in the desired cylindical coordinate space 
    ## - displace the calculated point so that the coil is in the center.
    displacements = np.array(list(map(lambda x:x.position , coils))) # list of every position attribute in the coil container
    axes = np.array(list(map(lambda x:x.axis, coils)))
    radii = np.array(list(map(lambda x:x.radius, coils)))
    out = []
    for point in grid:
        inputs = np.array(list(map(lambda x: x + point, displacements)))
        mag = []
        for i in range(len(inputs)):
            inp_rotated = coil2origin(inputs[i], axes[i])
            z, r, r1 = bob_e(inp_rotated, convert=True, radius=radii[i])
            mag.append(np.linalg.norm([z, r]))
        out.append(np.log(sum(mag)))

    out = np.array(out).reshape((100,100))
    return out


def fx_calc(points):
    """
    Since I don't want to break anything from before but I want to try new things,
    this has a duplicate function of plugging in input points into the bob_e function.

    Used in the graph_fx_contour function in the plotting section.
    """
    #print(points)
    r_z = []
    z_z = []
    sum = []
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(bob_e, point, convert=False): point for point in points}
        #print(len(futures))
        
        for index, task in enumerate(futures):
            result = task.result()
            r_z.append(abs(result[1]))
            z_z.append(abs(result[0]))
            sum.append(abs(result[0] + result[1]))
    
    return {
        "rho_z" : r_z,
        "zeta_z" : z_z
    }

    

##################
# PLOTTING FUNCS #
##################
def graph_fx_contour():
    """
    A contour graph of the fZeta or the fRho components side by side.
    """
    # Create coils
    ## Assumes a single coil in the XY plane
    c = coil(radius=1, x=0, y=0, z=0, axis="XY")

    # Create plots
    plot = plt.figure()
    ax_zeta = plot.add_subplot(121)
    ax_rho = plot.add_subplot(122)

    # Resolution parameters - determines fidelity of graph
    resolution = 100 # determines the number of points created between the bounds
    
    x_l = -3
    x_u = 3

    y_l = 0
    y_u = 3


    ## Construct grid
    x_linspace = np.linspace(x_l, x_u, resolution)
    y_linspace = np.linspace(y_l, y_u, resolution)
    z_linspace = np.zeros(resolution**2)

    gX,gY = np.meshgrid(x_linspace, y_linspace)
    points = np.column_stack(np.vstack([gY.ravel(), z_linspace, gX.ravel()]))

    z_data = fx_calc(points)
    #print(z_data["rho_z"])
    #print(z_data["zeta_z"])
    Z_Z = np.array(z_data["zeta_z"]).reshape(resolution, resolution)
    R_Z = np.array(z_data["rho_z"]).reshape(resolution, resolution)
    print(R_Z.ravel().min())
    print(R_Z.ravel().max())
    zmesh = ax_zeta.contourf(x_linspace, y_linspace, Z_Z, levels=100,
                             cmap="gist_ncar")
    rmesh = ax_rho.contourf(x_linspace, y_linspace, R_Z, levels=100,
                            cmap='gist_ncar')
    plot.colorbar(zmesh, ax=ax_zeta)
    plot.colorbar(rmesh, ax=ax_rho)

    plt.show()




def graph_multiple():
    '''
    A Contour graph that shows a 2D example in world space.
    Graphs |E|.
    '''
    # Create coils
    # Assumed that the coils are in the Y-Z plane
    c0 = coil(radius=1, x=-1.5, y=0, z=0, axis='YZ')
    c1 = coil(radius=1, x=1.5, y=0, z=0, axis='YZ')
    c0_a = coil(radius=0.5, x=-1.5, y=0, z=0, axis="YZ")
    c1_a = coil(radius=0.5, x=1.5, y=0, z=0, axis="YZ")
    coils = [c0, c1, c0_a, c1_a] # container for all the coils added to the configuration.

    # Create plots
    plot = plt.figure()
    ax = plot.add_subplot(111)

    # Create Grid
    global data, grid_zetas

    ## clear data just in case
    data = {}

    ## Below function call creates cyl coordinates from -3 to 3 with the desired zetas.
    # GenerateGrid(-3, 3, 100, grid_zetas)

    ## Below, the code will create a 2D meshgrid of cartesian coordinates. 
    x1 = np.linspace(-2,2,100)
    y1 = np.linspace(-3,3,100)

    gx,gy = np.meshgrid(x1, y1) ## x and y grid components
    grid = np.column_stack(np.vstack([gx.ravel(), np.zeros(10000), gy.ravel()]))

    #print(np.array(grid).shape)

    # Run Calculations
    fz_out = calc_E(grid, coils)
    #fz_out = np.array(fz_out)
    #levels = np.linspace(z.min(), z.max(), 10)
    #print(fz_out)

    mesh = ax.pcolormesh(x1,y1,fz_out, cmap='gist_rainbow')
    plot.colorbar(mesh, ax=ax)
    
    #plt.legend(loc="right", ncol = 1)
    plt.show()



def graph_doc_recreation():
    '''
    Verifying graphs that replicate documentation results
    '''
    plot = plt.figure()
    ax = plot.add_subplot(121)
    ax1 = plot.add_subplot(122)

    out = []
    out1 = []
    vals = list(data.values())
    for i in range(len(vals)):
        out.append([])
        out1.append([])
        for point in vals[i]:
            z, r, r1 = bob_e(point, convert=False)
            #print(f"zeta: {z}")
            #print(f"rho: {r}")
            out[i].append(np.array([r1, z]))
            out1[i].append(np.array([r1, r]))
    out = np.array(out)
    out1 = np.array(out1)
    labs = list(data.keys())

    for i in range(len(out)):
        x = out[i][:,0]
        y = out[i][:,1]
        #print(f"zeta: {y}")
        label = labs[i]
        ax.plot(x,y,label=label)
    for i in range(len(out1)):
        x = out1[i][1:,0]
        y = out1[i][1:,1]
        #print(f"rho: {y}")
        label = labs[i]
        ax1.plot(x,y,label=label)

    plt.legend(loc="right", ncol = 1)
    ax.set_title("Fzeta")
    ax1.set_title(f"Frho")
    ax.set_xlabel("rho")
    ax1.set_xlabel("rho")
    ax.set_ylim(0,10e2)
    #ax1.set_ylim(-10, 10)

    plt.show()

####################
# GRAPHICS CONTROL #
####################
"""
Function call below will determine what is graphed.
"""

graph_fx_contour()
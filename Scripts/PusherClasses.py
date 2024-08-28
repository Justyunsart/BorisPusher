# Global classes and structures that many scripts rely on.
# Made to streamline coupling

from dataclasses import dataclass
from magpylib.current import Circle as C
from magpylib import Collection
import numpy as np

from sympy import solve, Eq, symbols, Float

#===========#
# Dataclass #
#===========#
'''
The struct-like data class that will be stored inside an array (Array of structs data structure, or AoS)
Makes the data, code more intuitive.

I made the pos, vel, and b fields separate floats because pandas really hates it when cells are containers; doing any manipulation of data
was causing me immense agony and pain. It makes particle instantiation really ugly... Too bad!
'''
@dataclass
class particle:
    id: int
    step: int
    
    #position
    px: np.float64
    py: np.float64
    pz: np.float64

    # Velocity
    vx: np.float64
    vy: np.float64
    vz: np.float64

    # B field
    bx: np.float64
    by: np.float64
    bz: np.float64

@dataclass
class charge:
    position: np.ndarray
    q: float

#========#
# Fields #
#========#
EfOptions = np.array(["Zero", "Static", "Calculated"])
BfOptions = np.array(["Zero", "Static", "Calculated"])

#=========#
# Current #
#=========#
# creates a square box of Loop coils
def Circle(a, dia, d, gap):
    # current Loop creation, superimpose Loops and their fields
    s1 = C(current=a, diameter=dia).move([-(d/2)-gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s2 = C(current=-a, diameter=dia).move([(d/2)+gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s3 = C(current=-a, diameter=dia).move([0,-(d/2)-gap,0]).rotate_from_angax(90, [1, 0, 0])
    s4 = C(current=a, diameter=dia).move([0,(d/2)+gap,0]).rotate_from_angax(90, [1, 0, 0])
    s5 = C(current=a, diameter=dia).move([0,0,-(d/2)-gap]).rotate_from_angax(90, [0, 0, 1])
    s6 = C(current=-a, diameter=dia).move([0,0,(d/2)+gap]).rotate_from_angax(90, [0, 0, 1])

    c = Collection(s1,s2,s3,s4,s5,s6, style_color='black')
    return c


# helmholtz setup for a test
def Helmholtz(a, dia, d):
    # helmholtz test
    s7 = C(current=a, diameter=dia).move([-(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])
    s8 = C(current=a, diameter=dia).move([(d/2),0,0]).rotate_from_angax(90, [0, 1, 0])

    c = Collection (s7, s8)
    return c

def GetCurrentTrace(c:Collection, dia:int, res:int):
    rad = dia/2
    # need to figure out what axis the slices are
    points = []
    for current in c.children:
        # Find the direction the circle is facing, for science.
        orientation = current.orientation.as_euler('xyz', degrees=True)

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
                pointc = charge(position=point, q=current.current)
                points.append(pointc)

                # rotate!!! for more! points!
                point = np.zeros(3, dtype=float)
                point[xl] = j
                point[yl] = s
                point[zl] = center[zl]
                pointc = charge(position=point, q=current.current)
                points.append(pointc)

    return np.asarray(points)
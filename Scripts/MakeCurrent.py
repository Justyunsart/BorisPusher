'''
Script that handles the creation of the current coils used in the simulation.

'''
from magpylib.current import Circle as C
from magpylib import Collection

#==============#
# CONSTRUCTION #
#==============#
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

##############
# PARAMETERS #
##############
a = 5 * 10e5 # current in terms of A
dia = 2. # coil diameter
d = 2. # coil placement

###########
# CURRENT #
###########
'''
current: var that references a magpylib current/ collection object. This is passed to many different files that utilizes it.

Note:
Do not change the name of the var current; only change the function it calls. This is because the var is referenced by name.
'''
#current = Circle(a, dia, d, gap)
current = Helmholtz(a, dia, d * 2) # mirror, since distance is far enough to not make helmholtz

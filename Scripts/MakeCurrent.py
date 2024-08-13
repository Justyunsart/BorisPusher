# Creates the current used in the simulation.
# Idk if this should be its own file but oh well, at least we can access the current without running the boris pusher script.

from PusherClasses import Circle

# physics variables
a = 1.0e5 # current
aa = a / 1.72 # triangle current
dia = 500. # coil diameter
d = 800. # coil placement
l = 600 # line space(x, y, z variables)
r = 100 # line space increments
gap = 15 # sets space between coils


current = Circle(a, dia, d, gap)
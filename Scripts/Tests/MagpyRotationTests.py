"""
Place to play around with how to access and manipulate the scipy Rotation objects 
utilized by magpylib's Orientations parameter
"""
from magpylib.current import Circle
import magpylib as mpl
from scipy.spatial.transform import Rotation as R
import numpy as np

# Create circular coils.
coil = Circle(position=(0,0,0), diameter=2)
coil1 = Circle(position=(0,0,1), diameter=2)

# Rotate the circle
coil.rotate_from_angax(45, "y")
coil1.rotate_from_angax(90, "y")

# Add them to a collection object.
c = mpl.Collection()
c.add(coil, coil1)

# 1. Accessing the rotations object from inside a collection.
#    - We can even inverse the rotation with scipy methods.
for coil in c.children_all:
    rotation = coil.orientation
    inv_rotation = rotation.inv().as_euler('xyz', degrees=True)
    #print(f"Child {coil} has orientation: {rotation.as_euler('xyz', degrees=True)}")
    coil.rotate_from 



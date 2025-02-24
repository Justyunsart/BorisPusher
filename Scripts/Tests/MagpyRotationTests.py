"""
Place to play around with how to access and manipulate the scipy Rotation objects 
utilized by magpylib's Orientations parameter
"""
from magpylib.current import Circle
import magpylib as mpl
from scipy.spatial.transform import Rotation as R
import numpy as np

# config
coilPos = np.array([3,2,1])
sensorPos = np.array([2,3,1])
rotationDeg = 45
rotationAxis = 'y'

# Create circular coil
coil = Circle(position=coilPos, diameter=2)

# And a random test point
sensor = mpl.Sensor(position=sensorPos)

# Rotate the circle
coil.rotate_from_angax(rotationDeg, rotationAxis)

# STEP 1: MOVE COIL TO ORIGIN
# make a copy of the original coil and sensor
coil1 = coil
sensor1 = sensor
# 1st get the inverse rotation
rot = coil.orientation
inv_rot = R.inv(rot).as_euler('xyz', degrees=True)
# move both the copy and the sensor so that the coil is centered at the origin
coil1.position = np.linspace(coilPos, (0,0,0), 50)
sensor1.position = np.linspace(sensorPos, sensorPos-coilPos, 50)
# then rotate both objects by the inverse rotation of the original coil
# apply rotations
coil1.rotate_from_euler(np.linspace(0, inv_rot, 50), 'xyz')
sensor1.rotate_from_euler(np.linspace(0, inv_rot, 50), 'xyz', anchor=(0,0,0))

mpl.show(coil1, sensor1, animation=True, backend='plotly')




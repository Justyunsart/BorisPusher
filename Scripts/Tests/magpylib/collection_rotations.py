
"""
How does magpylib.collections store multiple rotations on a coil? as a list or as a combined thing?
"""
import magpylib as mp
from magpylib import Collection
from magpylib.current import Circle

    # create coil and rotate it several times
circle = Circle(position=(0,0,0), current=100, diameter=1)
circle.rotate_from_angax(90, 'x')
circle.rotate_from_angax(90, 'y', anchor=circle.position)
circle.rotate_from_angax(20, 'x', anchor=circle.position)

    # add the circle to a Collection and then access its orientation
collection = Collection()
collection.add(circle)

for c in collection:
    print(c.orientation.as_euler('xyz', degrees=True))

mp.show(collection)
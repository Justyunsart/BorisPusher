
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
    pass
    #print(c.orientation.as_euler('xyz', degrees=True))

#mp.show(collection)


def OrientPoint(c: Circle, point):
    """
    Points plugged into the self.at function need to be transformed to be in the assumed config.
    """
    # Reset rotation to identity
    rotation = c.orientation
    print(f"coil rotation: {rotation.as_euler('xyz', degrees=True)}")
    # subtract the coil's position from the rotated point to make it centered at the origin.
    # after subtracting, the rotation then can be applied. This makes the point rotate about the coil center.
    inv_rotation = rotation.inv()
    rotated_point = inv_rotation.apply(point - c.position)

    print(f"started with {point}, ended with {rotated_point}")
    return rotated_point

if __name__ == '__main__':
    import numpy as np
    circle = Circle(position=(0, 0, 0), current=100, diameter=1)
    circle.rotate_from_angax(90, 'x')


    p = np.array((0,2,0))
    rotated_p = OrientPoint(circle, p)

    print(rotated_p)
from magpylib import Collection
from magpylib.current import Circle

"""
Contains a definition for a generic magpylib.Collection object to use for testing.
"""
def mirror():
    c = Collection()
    
    # create circles
    c1 = Circle(position=(-1,0,0), current=1000, diameter=1)
    c1.rotate_from_angax(90, 'y')
    c2 = Circle(position=(1,0,0), current=1000, diameter=1)
    c2.rotate_from_angax(90, 'y')
    
    # add circle to collection
    c.add(c1)
    c.add(c2)

    return c
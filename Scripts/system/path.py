import os
from system.Observer import Data

"""
generic class for path variables. Contains a string attribute and a method to update when notified by observer pattern

PARAMETERS:
path: the full path the class is referencing
name: used for when the path gets updated, the name of the DIR at the end of the path
"""
class Path():
    def __init__(self, path, name):
        self.name = name
        self.path = Data(name)
        self.path.data = path

    """
    called by observer
    """
    def update(self, value):
        print(f"system.path.Path.update: the new observed value is: {value}")
        self.path.data = os.path.join(value, self.name)
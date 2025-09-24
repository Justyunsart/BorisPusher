from abc import ABC, abstractmethod
from magpylib.current import Circle as C
from magpylib import Collection

"""
Holds presets for magpylib coil configs.
These are created upon button press on the coils window.

Also, creating a config through these presets will mark it with a custom
metadata field showing what configuration it is.

The func. that dictates how to create input files from these configured presets
are in Gui_tkinter.widgets.CurrentGuiClasses.CurrentEntryTable
"""

coil_cust_attr_name = "user.coil_config_type" # the name of the custom attribute


"""
an intermediary container class that holds numbers only;
the CircleCurrentConfig class has GUI dependencies
"""
class circle_params():
    def __init__(self, px=0, py=0, pz=0, amp=1000, dia=1, rot_ang=[], rot_ax=[], inner=0):
        self.PosX = px
        self.PosY = py
        self.PosZ = pz
        self.Q = amp
        self.Diameter = dia
        self.RotationAngle = rot_ang
        self.RotationAxis = rot_ax
        self.Inner_r = inner

class preset_hexahedron():
    # params defined below. Can turn into function args if u want them to be programmable.
    offset = 1.1 # meters
    amp = 1000 # current absolute value, in amperes
    dia = 1

    name = "hexahedron" # default file name

    _attr_val = b"hexahedron" # custom file metadata value

    config =  [circle_params(px=offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y'], inner=0),
     circle_params(px=-offset, py=0, pz=0, amp=-amp, dia=dia, rot_ang=[90], rot_ax=['y'], inner=0),
     circle_params(px=0, py=offset, pz=0, amp=amp, dia=dia, rot_ang=[-90], rot_ax=['x'], inner=0),
     circle_params(px=0, py=-offset, pz=0, amp=-amp, dia=dia, rot_ang=[-90], rot_ax=['x'], inner=0),
     circle_params(px=0, py=0, pz=offset, amp=amp, dia=dia, rot_ang=[], rot_ax=[], inner=0),
     circle_params(px=0, py=0, pz=-offset, amp=-amp, dia=dia, rot_ang=[], rot_ax=[], inner=0)]

class preset_mirror():
    # params defined below. Can turn into function args if u want them to be programmable.
    offset = 1.1 # meters
    amp = 1000 # current absolute value, in amperes
    dia = 1

    name = "mirror" # default file name

    _attr_val = b"mirror"

    config =  [circle_params(px=offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y']),
     circle_params(px=-offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y'])]

class preset_cusp():
    # a mirror coil with opposing currents so that it's a cusp now.
    # params defined below. Can turn into function args if u want them to be programmable.
    offset = 1.1 # meters
    amp = 1000 # current absolute value, in amperes
    dia = 1

    name = "cusp" #default file name

    _attr_val = b"cusp"

    config = [
        circle_params(px=offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y']),
        circle_params(px=-offset, py=0, pz=0, amp=-amp, dia=dia, rot_ang=[90], rot_ax=['y'])
    ]
"""
Classes that hold the constructor of the magpylib.Collection object that corresponds to shape.
Done so that labelling of used shapes is done via classes and not functions.
"""
class CoilShapeConstructor(ABC):
    @classmethod
    def create(cls, offset, q, dia):
        """
        returns the magpylib collections object that holds data.
        """
        pass
# INSTANTIATION
class HexConstructor(CoilShapeConstructor):
    @classmethod
    def create(cls, offset, q, dia):
        # current Loop creation, superimpose Loops and their fields
        s1 = C(current=q, diameter=dia).move([-offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])
        s2 = C(current=-q, diameter=dia).move([offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])
        s3 = C(current=-q, diameter=dia).move([0, -offset, 0]).rotate_from_angax(-90, [1, 0, 0])
        s4 = C(current=q, diameter=dia).move([0, offset, 0]).rotate_from_angax(-90, [1, 0, 0])
        s5 = C(current=q, diameter=dia).move([0, 0, -offset]).rotate_from_angax(90, [0, 0, 1])
        s6 = C(current=-q, diameter=dia).move([0, 0, offset]).rotate_from_angax(90, [0, 0, 1])

        c = Collection(s1, s2, s3, s4, s5, s6, style_color='black')
        return c

class HelmholtzConstructor(CoilShapeConstructor):
    @classmethod
    def create(cls, offset, q, dia):
        s7 = C(current=q, diameter=dia).move([-offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])
        s8 = C(current=q, diameter=dia).move([offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])

        c = Collection(s7, s8)
        return c

"""
Classes for the actual presets.
The class CoilPreset will hold UNIVERSAL settings
and subclasses will add unique attributes.
"""
class CoilPreset(ABC):
    """
    abstract class for presets.
    contains parameters that exist for every single preset.
    """
    def __init__(self, offset, q, dia, shape:CoilShapeConstructor):
        self.offset = offset
        self.q = q
        self.dia = dia
        self.shape = shape #contains the method to create the collection of given shape

    @abstractmethod
    def create_preset(self):
        pass

class WasherPreset(CoilPreset):
    """
    Subclass of CoilPreset that also contains the inner radius attribute.
    Stored as a list of size len(collection), which contains the same order.
    """




    # What gets created whenever the program needs to create a new coils input file due to the coils dir having no other files.
default_coil = preset_hexahedron
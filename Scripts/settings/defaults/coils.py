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




    # What gets created whenever the program needs to create a new coils input file due to the coils dir having no other files.
default_coil = preset_hexahedron
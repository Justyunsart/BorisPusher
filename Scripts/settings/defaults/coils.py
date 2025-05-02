from Gui_tkinter.funcs.GuiEntryHelpers import CircleCurrentConfig

"""
Holds presets for magpylib coil configs
"""

"""
an intermediary container class that holds numbers only;
the CircleCurrentConfig class has GUI dependencies
"""
class circle_params():
    def __init__(self, px=0, py=0, pz=0, amp=1000, dia=1, rot_ang=[], rot_ax=[]):
        self.PosX = px
        self.PosY = py
        self.PosZ = pz
        self.Amp = amp
        self.Dia = dia
        self.Rot_ang = rot_ang
        self.rot_ax = rot_ax

class preset_hexahedron():
    # params defined below. Can turn into function args if u want them to be programmable.
    offset = 1.1 # meters
    amp = 1000 # current absolute value, in amperes
    dia = 1

    name = "hexahedron" # default file name

    config =  [circle_params(px=offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y']),
     circle_params(px=-offset, py=0, pz=0, amp=-amp, dia=dia, rot_ang=[90], rot_ax=['y']),
     circle_params(px=0, py=offset, pz=0, amp=-amp, dia=dia, rot_ang=[90], rot_ax=['x']),
     circle_params(px=0, py=-offset, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['x']),
     circle_params(px=0, py=0, pz=offset, amp=amp, dia=dia, rot_ang=[], rot_ax=[]),
     circle_params(px=0, py=0, pz=-offset, amp=-amp, dia=dia, rot_ang=[], rot_ax=[])]

class preset_mirror():
    # params defined below. Can turn into function args if u want them to be programmable.
    offset = 1.1 # meters
    amp = 1000 # current absolute value, in amperes
    dia = 1

    name = "mirror" # default file name

    config =  [circle_params(px=offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y']),
     circle_params(px=-offset, py=0, pz=0, amp=amp, dia=dia, rot_ang=[90], rot_ax=['y'])]
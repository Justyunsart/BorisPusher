import tkinter as tk
from tkinter import ttk
import itertools
from Gui_tkinter.widgets.layout import *
from presets import *
from enum import Enum
from magpylib import Collection

"""
Make an explicit protocol for creating a new file instead of doing it implicitly.
This means making a window pop up with a button press that lets you configure and name a file.

This window needs information like:
- Name of new file
- Dataclass of the new file (What fields exist?)
- Presets?
"""

class NewFileWindow(tk.Toplevel):
    """
    this is a tk.Toplevel subclass because the new file dialogue would likely need to be contained in a
    popup window.
    """
    # It's alright to have lots of arguments, as long as the MANDATORY ones are kept at a minimum
    def __init__(self, parent:tk.Tk, contextual_widgets:tk.Frame=None, title:str="New File Window", presets:Enum=None, *args, **kwargs):
        """
        parent: the object that owns this window (most likely a tkinter application instance, root)
        contextual_widgets: externally provided series of widgets (must also have their own complete implementation
        outside this class) that can optionally be displayed in this window also.
            - class must be functional with or without this argument
            - this class should only display the widgets
                > contextual_widget arguments should probably implement the same interface so that appropriate funcs
                  can be abstracted when calling.
        """
        # pass any special arguments to the tkinter toplevel constructor.
        super().__init__(parent, *args, **kwargs)
        self.title(title)
        self.geometry("800x400")
        # Root window must also allow its single cell to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Make the frame where all other frames go
        # Reminder: MarginalFrame is a tk.Frame subclass that has header, body, footer attributes.
        #   - defined in Gui_tkinter.widgets.layout.
        self.main_frame = MarginalFrame(self)

        # Adjust the layout of the frames as desired (if you even desire)
        self.main_frame.footer.layout = JustifyHorizontal

        self.presets = presets

        # Then add the rest of the contents
        # HEADER
        self.main_frame.insert_text("New Input File", self.main_frame.header) # Header (title)

        # BODY
        # remember that the body frame needs manual packing by default.
        # consider adding subframes inside it if you want layouts.

        #   BODY - NAME ENTRY
        self.universal_settings_frame = tk.Frame(self.main_frame.body)
        self.name_entry_frame = tk.Frame(self.universal_settings_frame)
        self.entry_name = tk.Label(self.name_entry_frame, text="Name: ")
        self.entry_var = tk.StringVar()
        self.entry_widget = tk.Entry(self.name_entry_frame, textvariable=self.entry_var)

        #   BODY - LISTBOX
        self.listbox_frame = tk.Frame(self.main_frame.body)
        self.listbox_title = tk.Label(self.listbox_frame, text="Presets: ")
        self.listbox = tk.Listbox(self.listbox_frame)

        # SEPARATOR BETWEEN BODIES
        separator = ttk.Separator(self.universal_settings_frame, orient=tk.HORIZONTAL)

        # BODY - CONTEXTUAL
        if contextual_widgets:
            # only create stuff if contextual_widgets is populated (not None)
            self.contextual_widgets = contextual_widgets(self.universal_settings_frame)
            self.contextual_widgets.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        #   BODY - PACKING
        #       big frame placement
        self.listbox_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.universal_settings_frame.pack(side=tk.TOP, fill="both", expand=True)

        #       name entry
        self.name_entry_frame.pack(side=tk.TOP, anchor=tk.NW, expand=True)
        self.entry_name.pack(side=tk.LEFT)
        self.entry_widget.pack(side=tk.LEFT)

        #       separator
        separator.pack(side=tk.TOP, fill='x', expand=True)

        #       listbox
        self.listbox_title.pack(side=tk.TOP, fill='x')
        self.listbox.pack(side=tk.TOP, fill="both", expand=True)

        # FOOTER
        self.button_confirm = self.main_frame.insert_widget(tk.Button, self.main_frame.footer,
                                                            text="Confirm")
        self.button_cancel = self.main_frame.insert_widget(tk.Button, self.main_frame.footer,
                                                            text="Cancel")
        # packing
        #self.main_frame.grid(row=0, column=0, sticky="nsew")
        #self.update_idletasks()
        # ANY OTHER UPDATES BFORE FINISHING INIT
        self.populate_presets()
        self.listbox.bind("<<ListboxSelect>>", self.on_preset_select)

    def populate_presets(self):
        """presets are shown in the listbox widget all the way right of the window."""
        if self.presets:
            # for this function to do anything, the user must provide a preset Enum.

            # if a preset enum is provided, then include all fo the enum keys in the listbox
            for item in self.presets:
                self.listbox.insert(tk.END, item.name)

    def on_preset_select(self, event, *args, **kwargs):
        widget = event.widget #listbox widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            value = widget.get(index)
            if self.contextual_widgets:
                self.contextual_widgets.information = getattr(self.presets, value).value

    def _debug_information(self, *args, **kwargs):
        """prints out the contextwidget's information property"""
        print(self.contextual_widgets.information)

# contextual widgets defined below
# these are stored as self-contained frames, representing unique settings belonging to certain things.
from abc import ABC, abstractmethod
class ContextualWidget(ABC, tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # This list will be iterated through to extract and inject information.
        # (like when working with presets)
        self.info_widgets = [] # a list that will contain all relevant information-holding widgets.

    """
    Interface so that you can access the parameters the widget is responsible for (read and write)
    This is done so that presets can just involve calling this property.
    """
    @property
    def information(self):
        """print out all the data (value held by vars)"""
        out = [w.get() for w in self.info_widgets]
        return out
    @information.setter
    def information(self, value):
        """When you want to replace all parameter values at once (instead of one at a time)"""
        for i in range(len(value)):
            self.info_widgets[i].set(value[i])

class ParticleContext(ContextualWidget):
    """
    Unique settings for configuring particles:
        - position (x, y, z)
        - velocity (vx, vy, vz)
    """
    class xyzSetting(tk.Frame):
        """
        shortcut to populate frame with labelled entries for xyz parameters.
        """
        class LabelledEntry(tk.Frame):
            """a tkinter widget that contains a label next to an entry."""

            def __init__(self, parent, text, *args, **kwargs):
                super().__init__(parent, *args, **kwargs)
                self.text = text
                self.var = tk.StringVar()
                self.label = tk.Label(self, text=self.text)
                self.entry = tk.Entry(self, textvariable=self.var)

                # packing
                self.label.pack(side=tk.LEFT, expand=True)
                self.entry.pack(side=tk.LEFT, expand=True)

            def get(self):
                return self.entry.get()

        def __init__(self, parent, title, *args, **kwargs):
            super().__init__(parent, *args, **kwargs)
            self.title = title

            # Display title as a tk.Label
            self.title_label = tk.Label(self, text=title)
            self.title_label.pack(side=tk.TOP, fill='x')

            self.x = self.LabelledEntry(self, "x")
            self.y = self.LabelledEntry(self, "y")
            self.z = self.LabelledEntry(self, "z")

            self.x.pack(side=tk.LEFT, expand=True)
            self.y.pack(side=tk.LEFT, expand=True)
            self.z.pack(side=tk.LEFT, expand=True)

        def get_vars(self):
            return self.x.var, self.y.var, self.z.var

        def get(self):
            """Output is ordered x, y, z"""
            return self.x.get(), self.y.get(), self.z.get()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # position
        self.position = self.xyzSetting(self, "Position")

        # velocity
        self.velocity = self.xyzSetting(self, "Velocity")

        # packing
        # velocity and position frames get equal spacing between each other
        self.position.pack(side=tk.TOP, fill="both", expand=True)
        self.velocity.pack(side=tk.TOP, fill="both", expand=True)

        # Flattened list of x, y, z tk.String_var objects
        # position xyz, then velocity xyz.
        self.info_widgets = list(itertools.chain(*[self.position.get_vars(), self.velocity.get_vars()]))


class RingContext(ContextualWidget):
    """
    This one has more automation compared to the particle contextual widgets,
    as this assumes that all the rings in the configuration operate under
    the same parameters.

    There is also a dropdown / optionmenu that lets the user choose the chape of the configuration as well,
    which informs the number and orientation of the config when constructed.
    """
    # TODO: bring the shape options + constructor information from centralized area
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # SHAPES
        shape_frame = tk.Frame(self)

        # hardcode shape options for now
        shapes = ('hexahedron', 'helmholtz')
        # Optionmenu to show the current configurable shapes
        shape_label = tk.Label(shape_frame, text="Shape: ")
        self.shape_var = tk.StringVar()
        self.shape_menu = tk.OptionMenu(shape_frame, self.shape_var, *shapes)

        # OFFSET
        self.entry_frame = tk.Frame(self)
        offset_label = tk.Label(self.entry_frame, text="Offset: ")
        self.offset_var = tk.StringVar()
        self.offset_entry = tk.Entry(self.entry_frame, textvariable=self.offset_var)

        # CHARGE
        charge_label = tk.Label(self.entry_frame, text="Charge: ")
        self.charge_var = tk.StringVar()
        self.charge_entry = tk.Entry(self.entry_frame, textvariable=self.charge_var)

        # DIAMETER
        self.entry_frame_2 = tk.Frame(self)
        self.diameter_var = tk.StringVar()
        diameter_label = tk.Label(self.entry_frame_2, text="Diameter: ")
        self.diameter_entry = tk.Entry(self.entry_frame_2, textvariable=self.diameter_var)

        # packing
        shape_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.entry_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.entry_frame_2.pack(side=tk.TOP, fill="both", expand=True)

        shape_label.pack(side=tk.LEFT)
        self.shape_menu.pack(side=tk.LEFT, fill='x', expand=True)

        offset_label.pack(side=tk.LEFT)
        self.offset_entry.pack(side=tk.LEFT, fill='x', expand=True)

        charge_label.pack(side=tk.LEFT)
        self.charge_entry.pack(side=tk.LEFT, fill='x', expand=True)

        diameter_label.pack(side=tk.LEFT)
        self.diameter_entry.pack(side=tk.LEFT, fill='x', expand=True)

        self.info_widgets = [self.shape_var, self.offset_var, self.charge_var, self.diameter_var]

class WasherContext(RingContext):
    """Same as the RingContext, with the addition of an inner_r param"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # inner_r
        inner_r_label = tk.Label(self.entry_frame_2, text="Inner radius: ")
        self.inner_r_var = tk.StringVar()
        self.inner_r_entry = tk.Entry(self.entry_frame_2, textvariable=self.inner_r_var)
        self.entry_frame_2.pack(side=tk.TOP, expand=True)
        inner_r_label.pack(side=tk.LEFT)
        self.inner_r_entry.pack(side=tk.LEFT, expand=True)

        self.info_widgets.append(self.inner_r_var)

"""
OK, BUT HOW DO YOU GO FROM FILLED OUT VARIABLES IN THE NEW FILE DIALOG TO A CSV FILE


Classes that hold the constructor of the magpylib.Collection object that corresponds to shape.
Done so that labelling of used shapes is done via classes and not functions.


"""
class CoilShapeConstructor(ABC):
    @staticmethod
    def create(offset, q, dia, dataclass, *args, **kwargs):
        """
        returns the magpylib collections object that holds data.
        """
        pass
# INSTANTIATION
class HexConstructor(CoilShapeConstructor):
    @staticmethod
    def create(offset, q, dia, dataclass, alternate_q=True, *args, **kwargs):
        # alternate_q is a unique parameter because electric coil configs do not have alternating charges
        _q = q
        if alternate_q:
            _q = -q

        # current Loop creation, superimpose Loops and their fields
        s1 = dataclass(current=q, diameter=dia).move([-offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])
        s2 = dataclass(current=_q, diameter=dia).move([offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])
        s3 = dataclass(current=_q, diameter=dia).move([0, -offset, 0]).rotate_from_angax(-90, [1, 0, 0])
        s4 = dataclass(current=q, diameter=dia).move([0, offset, 0]).rotate_from_angax(-90, [1, 0, 0])
        s5 = dataclass(current=q, diameter=dia).move([0, 0, -offset]).rotate_from_angax(90, [0, 0, 1])
        s6 = dataclass(current=_q, diameter=dia).move([0, 0, offset]).rotate_from_angax(90, [0, 0, 1])

        c = Collection(s1, s2, s3, s4, s5, s6, style_color='black')
        return c

class HelmholtzConstructor(CoilShapeConstructor):
    @staticmethod
    def create(offset, q, dia, dataclass, *args, **kwargs):
        s7 = dataclass(current=q, diameter=dia).move([-offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])
        s8 = dataclass(current=q, diameter=dia).move([offset, 0, 0]).rotate_from_angax(90, [0, 1, 0])

        c = Collection(s7, s8)
        return c

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")

    newFileWindow = NewFileWindow(root, contextual_widgets=RingContext, presets=BRingPresets)
    newFileWindow.button_confirm.configure(command=newFileWindow._debug_information)


    root.mainloop()
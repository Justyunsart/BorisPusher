from abc import ABC, abstractmethod
import tkinter as tk
from system.bus import CommandBus

"""
Available Layouts:
    - JustifyLeft
    - JustifyRight
    - JustifyCenter
    - JustifyHorizontal
    - JustifyNull
I'm sure these are more or less self explanatory, but here are some words for you:
Left, Right and Center all stack widgets vertically. Horizontal assumes all widgets will fit in one row

Does this mean that you would need to create more frames, as you can't 'mix' multiple layouts in one frame? yes.
Is it a huge downside or even a bad thing? Probably not.

You can be more 'efficient' if placing everything manually, but the point of this approach is to be modular and 
automatic.
"""
# opt-in modifier (modular component for certain functions to avoid redundancy)
class LayoutWidget:
    """
    Interface for automating text insertion + formatting for layout-based widgets.
    Introduces functions to add texts.
    """
    def insert_text(self, text:str, frame, style = None):
        """
        expects the frame to have the function add(), like in the layout interface.
        Also, style has not been implemented yet.
        """
        text_widget = tk.Label(frame, text=text)
        frame.add(text_widget)

    def insert_widget(self, widget, frame, **kwargs):
        """
        kwargs = the arguments passed to the tkitner widget type passed.
        the function also returns a reference to the widget inserted into the frame.
        """
        widget = widget(frame, **kwargs)
        frame.add(widget)
        return widget

class Layout(ABC):
    """
    abstract base class for layout classes. They will automate widget placement by enforcing
    a programmed format.

    Expects that its only customers will be other tk.Frame subclasses because they're the main guys
    who are even interested and able to organize and place widgets.

    All of these classes should:
        - Never strictly enforce any changes in the component widgets
            - Placement WITHIN the frame (self) is fair game, but expect anything inside the component untouchable
        - Always be able to add widgets one at a time, and have dynamic layout organization.
            - class.add(widget) <- this should automatically format the widget in context to others.
        - Never pad (perpendicular to stacking direction): widgets touch edges of frame.
    """
    def __init__(self, frame):
        self.frame = frame
        self.widgets = [] #empty list that will hold all child widgets

    def add(self, widget):
        # Template Method - a non-abstract method calls the abstract method after some logic.
        #    - every time we add a widget to a layout, the internal widgets container should be updated.
        #    - done to avoid repeating the append call
        self.widgets.append(widget)
        self._relayout()

    def _relayout(self):
        """When there are multiple widgets added, reformat placement to account for it"""
        for idx, widget in enumerate(self.widgets):
            self._add(widget, idx)
    @abstractmethod
    def _add(self, widget, idx):
        """
        THE ACTUAL THING TO CHANGE IN SUBCLASSES - THE LOGIC OF PLACEMENT IS HERE
        add, then format, the widget inside the frame.
        """
        pass
# DEFINE LAYOUT CLASSES
class JustifyNull(Layout):
    """Tracks but does not place widgets"""
    def _add(self, widget, idx):
        pass

class JustifyCenter(Layout):
    """Every widget will be placed at the center of the frame in 1 column."""
    def _add(self, widget, idx):
        # Example: stack all widgets vertically centered

        widget.update_idletasks()
        widget.place(
            relx=0.5,
            rely=(idx + 1) / (len(self.widgets) + 1),  # spread out vertically
            anchor="center",
            relwidth=0.9/(idx+1)
        )

class JustifyLeft(Layout):
    """Align widgets to the left edge (stacked vertically)."""
    def _add(self, widget, index):
        spacing = 1 / (len(self.widgets) + 1)  # evenly spread vertically
        widget.place(relx=0.0, rely=(index + 1) * spacing, anchor="w")

class JustifyRight(Layout):
    """Align widgets right, stacking them horizontally."""
    def _add(self, widget, index):
        spacing = 1 / (len(self.widgets) + 1)
        widget.place(relx=1.0, rely=(index + 1) * spacing, anchor="e")

class JustifyHorizontal(Layout):
    """Evenly space all widgets in 1 row"""
    def _add(self, widget, index):
        spacing = 1 / (len(self.widgets) + 1)  # distribute across width
        widget.place(relx=(index + 1) * spacing, rely=0.5, anchor="center")

# CLASS DEFINITION FOR FRAMES THAT USE AUTO LAYOUTS!
# Technically these lines can also be directly added to any tk.Frame subclass, but this
# beats lots of redundancy.
class LayoutFrame(tk.Frame, LayoutWidget):
    def __init__(self, master, layout=JustifyNull, bus:CommandBus=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # store the layout this frame is programmed to use
        self._layout = layout(self)
        self.bus = bus
    """Add functionality to change layouts after init,"""
    @property
    def layout(self):
        return self._layout
    @layout.setter
    def layout(self, value):
        # not enforced, but make sure that the value is a valid layout class (defined in this file)!!

        # to change layouts, we also need to take the currently existing widgets and re-place them.
        widgets = self._layout.widgets
        self._layout = value(self) # we can overwrite the _layout attr AFTER storing the widgets in use.
        self._layout.widgets = widgets
        self._layout._relayout()

    # expose Layout.add to this class's namespace
    def add(self, widget):
        self._layout.add(widget)
        if self.bus is not None:
            self.bus.dispatch("reorder")

# General frame subclass preconfigured with a header, footer, and content frame.
# All of these frames will be of the LayoutFrame type with a null default layout, so that you can
# change layouts if you choose when making instances.
class MarginalFrame(tk.Frame, LayoutWidget):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # the main content frame is self.
        # Also set up the program to redo placements after widgets are added here.
        self.bus = CommandBus()
        self.bus.register("reorder", self.update)
        # inside self, make frames to organize header, footer, and body.
        self.header = LayoutFrame(self, layout=JustifyCenter, bus=self.bus, highlightbackground='red', highlightthickness=2)
        self.body = tk.Frame(self, highlightbackground='blue', highlightthickness=2) # not a LayoutFrame by default because manual control is most useful here
        self.footer = LayoutFrame(self, layout=JustifyCenter, bus=self.bus, highlightbackground='red', highlightthickness=2)
        # Though each frame will internally maintain placements, we also need to
        # place the frames themselves in self
        self.rowconfigure(0, weight=0, minsize=40)  # header doesn’t expand
        self.rowconfigure(1, weight=1)  # body expands
        self.rowconfigure(2, weight=0, minsize=40)  # footer doesn’t expand
        self.columnconfigure(0, weight=1)
        self.repack() # protocol to configure placements/grid

    def repack(self, *args, **kwargs):
        self.header.grid(row=0, column=0, sticky="nsew")
        self.body.grid(row=1, column=0, sticky="nsew")
        self.footer.grid(row=2, column=0, sticky="nsew")
        self.pack(side="top", fill="both", expand=True) # needed, otherwise window is blank until clicked and dragged.

    def refresh(self, *args, **kwargs):
        self.update_idletasks()
        self.update()
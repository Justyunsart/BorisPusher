from abc import ABC, abstractmethod
import tkinter as tk

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
        widget.place(
            relx=0.5,
            rely=(idx + 1) / (len(self.widgets) + 1),  # spread out vertically
            anchor="center"
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
class LayoutFrame(tk.Frame):
    def __init__(self, master, layout=JustifyNull, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # store the layout this frame is programmed to use
        self.layout = layout(self)

    # expose Layout.add to this class's namespace
    def add(self, widget):
        self.layout.add(widget)
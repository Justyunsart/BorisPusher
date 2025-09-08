
"""
class definitions for base level widgets
think of this as modifiers that any class can opt-in to for added functionality.

These classes should:
    - always focus on doing one thing really well - single responsibility
    - never / rarely couple with another class, unless there is a good reason
"""

class ParamWidget:
    """
    Functions necessary for widgets that need to save information to the main dataclass
    """
    @staticmethod
    def set_nested_field(obj, path, value):
        """Set a nested attribute given a dot-separated path"""
        #print(path)
        parts = path.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    @staticmethod
    def get_nested_field(obj, path):
        """Set a nested attribute given a dot-separated path"""
        parts = path.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        return getattr(obj, parts[-1])

class FileWidget:
    """
    Widgets that read input files (basically field method, particle widgets)

    There are some common attributes to maintain:
        - the input dir
        - acceptable presets (when creating new file)
    There are common functions too:
        - save file
        - load file (read csv)
        - create new file

    Because the way to track these things can vary by implementation, this class will only be limited
    to the backend functions. This class should never couple with specific GUI types/instances.
    """
    def __init__(self):
        # Initialize attributes (to be filled another time)
        self.input_dir = None
        self.presets = None

    # Value initialization is done MANUALLY because it will be easier to work with in some forms
    #   - If a widget has lots of these opt-in modifiers, it might get annoying to handle all the args expected.
    #   - This way, you have time to format inputs outside the __init__ call.
    # Remember to call this sometime in __init__ though!
    def fill_file_widget_attrs(self, input_dir, presets):
        self.input_dir = input_dir
        self.presets = presets

    # TODO: Move implementation in CurrentEntryTable here
    def save_file(self):
        pass

    def load_file(self):
        pass

    def create_file(self):
        pass
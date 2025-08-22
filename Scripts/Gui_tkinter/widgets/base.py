
"""
class definitions for base level widgets.
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
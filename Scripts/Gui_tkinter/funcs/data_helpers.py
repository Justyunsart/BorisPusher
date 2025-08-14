
"""
Helpers for some data structure operations
"""

def get_nested_value(d, keys):
    """
    Retrieves a value from a nested dictionary using a list of keys.

    Args:
        d (dict): The nested dictionary.
        keys (list): A list of keys representing the path to the desired value.

    Returns:
        The value at the specified path, or None if any key in the path is not found.
    """
    current_dict = d
    for key in keys:
        if isinstance(current_dict, dict) and key in current_dict:
            current_dict = current_dict[key]
        else:
            return None  # Key not found at this level
    return current_dict
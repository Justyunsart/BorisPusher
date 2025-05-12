"""
holds pleasing colors.
"""
from enum import Enum
from definitions import PLATFORM

# platform-dependent colors
match PLATFORM:
    case 'win32':
        transparent = '#000000'
    case 'darwin':
        transparent = "systemWindowBackgroundColor" 


class Drapion(Enum):
    # Broad GUI Frame colors
    Background = '#292929'
    Foreground = '#2D5D7B'
    Foreground_Bright = '#457EAC'
    Text = '#9191E9'
    Text_Bright = '#C2AFF0'
    # event-specific colors
    Warning_Highlight = '#E71D36' # used to showcase when something is bad. (red)
    Entry_Table_Cell_Highlight = '#0C090D' # what the border of an entrytable cell is when everything's fine. (black)
    Transparent_Highlight_Bg = transparent
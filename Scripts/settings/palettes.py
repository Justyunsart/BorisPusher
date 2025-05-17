"""
holds pleasing colors.
"""
from dataclasses import dataclass
from enum import Enum
from definitions import PLATFORM
from tkinter import font

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

"""
dataclass to associate a font.Font object with its respective color.
For convenience
"""
@dataclass
class Font_n_Color:
    font: font.Font
    color: str

"""
Text formatting for different text types
"""
def GUI_Fonts(master):
    return {
        'title' : Font_n_Color(font.Font(master=master, family='Roboto', size=18, weight='bold'),
                         Drapion.Background.value),
        'subtitle' : Font_n_Color(font.Font(master=master, family="Roboto", size=15, weight="bold"),
                            Drapion.Background.value),
        'body' : Font_n_Color(font.Font(master=master, family="Roboto", size=12, weight="normal"),
                            "black"),}
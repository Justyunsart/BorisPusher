from enum import Enum
"""
A centralized location for pop-up notification text and titles.
"""

class Title_Notif(Enum):
    warning = "Warning"

class Popup_Notifs(Enum):
    err_plot_missing_coil = "Coils.txt is missing or unreadable! Displaying empty collection."

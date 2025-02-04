from src.Settings.defaultSettings import names

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

"""
Contains the function that instantiates the QSettings class.
"""

def InitializeApp():
    # Initialize foundational application objects!
    GUIAPP = QApplication([])

    # Set organization, app names
    GUIAPP.setOrganizationName(names["Organization"])
    GUIAPP.setApplicationName(names["App"])

    # Create QSettings instance
    SETTINGS = QSettings()

    return GUIAPP, SETTINGS

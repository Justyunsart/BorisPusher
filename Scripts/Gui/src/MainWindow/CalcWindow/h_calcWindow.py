"""
The widget containing all the information needed for the calculation window of the program.
Will be a child of the central splitter widget of the main window.
Will also be controlled by Sidebar/h_sidebar.py to display some other stuff.
"""
from src.MainWindow.Sidebar.h_sidebar import Sidebar
from PySide6.QtWidgets import (QGroupBox, QLabel, QVBoxLayout)

class ParamTab(QGroupBox):
    """
    all the elements in the PARAMETERS tab of the calc window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Widgets creation
        label = QLabel("Params!")

        # Create Layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(label)
        self.setLayout(vlayout)

class CoilTab(QGroupBox):
    """
    all the elements in the COIL tab of the calc window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Widgets creation
        label = QLabel("Coils!")

        # Create Layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(label)
        self.setLayout(vlayout)


class CalcWindow_1(Sidebar):
    """
    todo: add functionality
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up pages
        ## Create tab widgets
        self.pg_param = ParamTab()
        self.pg_coils = CoilTab()
        ## Add tabs
        self.addPage(self.pg_param, "Params")
        self.addPage(self.pg_coils, "Coils")



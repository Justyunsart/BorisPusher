"""
The frame containing all logic for the plotting part of the program.
This will be a child of the central splitter widget of the main window.
"""
from PySide6.QtWidgets import (QGroupBox, QLabel, QVBoxLayout)

class PlotWindow(QGroupBox):
    """
    todo: add functionality
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Plotting Window")
        self.testLabel = QLabel("Plot!")

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.testLabel)
        self.layout = vlayout

"""
Custom class for the sidebar element of the main program.
It's going to inherit from QStackedWidget
"""
from PySide6.QtWidgets import (QStackedWidget, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout)
from PySide6.QtCore import QSettings
from ...Settings.defaultSettings import (defaults, names)

class Sidebar(QGroupBox):
    buttons = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Container for all the tab widgets
        self.pages = QStackedWidget()
        pageLayout = QVBoxLayout()
        pageLayout.addWidget(self.pages)
        # Container for all the buttons
        self.buttonBox = QGroupBox()
        self.buttonBoxLayout = QVBoxLayout()
        #self.buttonBox.setLayout(self.buttonBoxLayout)
        # Top level organization layout
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.buttonBoxLayout)
        self.mainLayout.addLayout(pageLayout)
        self.setLayout(self.mainLayout)

        # Read system settings to get font size
        self.labelSize = self.ReadSettings("Side Bar Font Size")
        #print(self.labelSize)

        # Apply the settings we just read
        #self.ApplySettings()
    
    def addPage(self, widget, name:str):
        """
        calls self.pages's addWidget() function, as well as 
        navigation buttons to move to it.
        """
        # Add the provided widget as the tab
        self.pages.addWidget(widget)

        # Create navigation button
        button = QPushButton()
        button.setText(name)
        ## Add button to the layout
        self.buttonBoxLayout.addWidget(button)
        #self.buttonBox.setLayout(self.buttonBoxLayout)
        ## Connect button to navigate tab
        ##     > assumes index of button in layout == index of page
        button.clicked.connect(lambda state, btn=button: self.move2Page(btn))

    def move2Page(self, btn):
        ind = self.buttonBoxLayout.indexOf(btn)
        #print(f'move button clicked {ind}')
        self.pages.setCurrentIndex(ind)
        
    def ReadSettings(self, name):
        """
        reads and applies appropriate settings related to the sidebar.
        """
        settings = QSettings(names["Organization"], names["App"])

        out = settings.value(name, defaults[name])
        return out

    def ApplySettings(self):
        newStyle = f"QTabBar::tab:!selected {{font-size:{self.labelSize}pt;}} QTabBar::tab:selected {{font-size:{self.labelSize}pt;}}"
        #self.tabBar().setStyleSheet(newStyle)
'''
Layout of the main window of the program.
Everything will all fall to this.
'''
import sys
from src.MainWindow.CalcWindow.h_calcWindow import CalcWindow_1
from src.MainWindow.PlotWindow.h_plotWindow import PlotWindow

from PySide6.QtWidgets import (QSplitter, QMainWindow, QApplication,
                               QVBoxLayout, QGroupBox)

from src.Settings.systemSettings import InitializeApp

if __name__ == ("__main__"):

    GUIAPP, SETTINGS = InitializeApp()

    # Create the central widget
    cenWid = QSplitter()
    # Add the windows
    vlayout = QVBoxLayout()
    tab = CalcWindow_1()
    vlayout.addWidget(tab)
    CWIN_OUT = QGroupBox()
    CWIN_OUT.setLayout(vlayout)

    vlayout = QVBoxLayout()
    tab = PlotWindow()
    vlayout.addWidget(tab)
    PWIN_OUT = QGroupBox()
    PWIN_OUT.setLayout(vlayout)


    cenWid.addWidget(CWIN_OUT)
    cenWid.addWidget(PWIN_OUT)

    # Create the main window
    main = QMainWindow()
    main.setCentralWidget(cenWid)

    # Display the window
    main.show()

    # Logic for closing
    sys.exit(GUIAPP.exec())
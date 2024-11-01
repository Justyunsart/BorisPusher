"""
All the logic that goes inside the field methods themselves.
"""
from GuiEntryHelpers import LabeledEntry
import tkinter as tk
from tkinter import ttk
import numpy as np

##############
# BASE CLASS #
##############
class FieldMethod():
    def __init__(self, master, widget):
        self.widget = widget(master)
    def graph(self, plot, fig, lim, *args):
        pass
    def ShowWidget(self):
        self.widget.ShowWidget()
    def HideWidget(self):
        self.widget.HideWidget()

class field_impl():
    listeners = []
    widgets = []
    frame1:tk.Frame = None
    def add_listener(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)
    def trigger_listener(self, *args):
        for listener in self.listeners:
            listener.update()
    def ShowWidget(self):
        self.frame1.grid()
    def HideWidget(self):
        self.frame1.grid_remove()
        

################
# GUI WIDGETS #
###############
class Fw_widget(field_impl):
    def __init__(self, frame):
        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)
        self.A = LabeledEntry(self.frame1, .1, row=1, col=0, title="A: ", width=10)
        self.B = LabeledEntry(self.frame1, .1, row=1, col=4, title="B: ", width=10)
        self.widgets = [self.A, self.B]
        
        self.A.value.trace_add("write", self.trigger_listener)
        self.B.value.trace_add("write", self.trigger_listener)
    

class Zero_widget(field_impl):
    def __init__(self, frame):
        self.frame1 = tk.Frame(frame)
        self.frame1.grid(row=2, column=0)
        self.X = LabeledEntry(self.frame1, 0, row=1, col=0, title="X: ", width=5, state="readonly")
        self.Y = LabeledEntry(self.frame1, 0, row=1, col=4, title="Y: ", width=5, state="readonly")
        self.Z = LabeledEntry(self.frame1, 0, row=1, col=8, title="Z: ", width=5, state="readonly")
        self.widgets = [self.X, self.Y, self.Z]

    

##################
# IMPLEMENTATION #
##################
class Fw_impl(FieldMethod):
    def __init__(self, master, widget=Fw_widget):
        super().__init__(master, widget)
    
    def graph(self, plot, fig, lim, *args):
        try:
            #print(f'A is: {self.A.value.get()}')
            #print(f'B is: {self.B.value.get()}')
            #print(f'Lim is: {lim}')
            A = float(self.widget.A.value.get())
            B = float(self.widget.B.value.get())

            lim = abs(lim)
            glim = 1.5 * lim
            x = np.linspace(-glim, glim, 50)
            # equation for fw_E
            E = np.multiply(A * np.exp(-(x / B)** 4), (x/B)**15)
            #print(f'X axis is: {x}')
            #print(f'Y axis is: {E}')
            plot.plot(x,E)
            
            # also plot vertical lines for where the coils are, for visual clarity
            plot.axvline(x = lim, color='r', linestyle='dashed')
            plot.axvline(x = -lim, color='r', linestyle='dashed')

        except ValueError:
            pass

class Zero_impl(FieldMethod):
    def __init__(self, master, widget=Zero_widget):
        super().__init__(master, widget)
    
    def graph(self, plot, fig, lim, *args):
        plot.axhline(y=0, color='b')

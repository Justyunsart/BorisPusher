from concurrent.futures import ProcessPoolExecutor #multiprocessing
import tkinter as tk
import time
import numpy as np

"""
Tests the capability of tkinter window to work alongside a multiprocessing function.
"""
class app():
    def __init__(self):
        self.root = tk.Tk()

        # widgets
        ## Frames
        self.main_frame = tk.Frame(self.root)
        ## Contents
        self.button = tk.Button(self.main_frame, text="Run Process")
        self.label = tk.Label(self.main_frame, text="")

        # packing
        self.main_frame.pack()
        self.button.pack()
        self.label.pack()

    def run_app(self):
        self.root.mainloop()

    def processed_method(self, **kwargs):
        start_process(self.root)

    

"""
emulates a long task that would be multiprocessed.
"""

def long_task(n):
    time.sleep(2)
    return n

def start_process(root):
    long_arr = np.arange(1000)
    with ProcessPoolExecutor() as executor:
        futures = executor.map(long_task, long_arr)
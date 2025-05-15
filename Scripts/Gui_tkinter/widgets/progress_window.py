import tkinter as tk
import threading
from multiprocessing import Manager


"""
a pop-up window created right after the 'calculate' button is pressed.
keeps track of simulation progress.
"""
class calculate_progress_window(tk.Toplevel):
    def __init__(self, parent: tk.Tk, queue):
        tk.Toplevel.__init__(self, parent)
            # multiprocessing manager
        self.result_queue = queue

            # window geometry
        self.parent = parent
        self.geometry("300x200")
        self.frame0 = tk.Frame(self)
        self.frame0.pack(fill=tk.BOTH, expand=1)

        self.step_var = tk.StringVar()

        ###########################################################
            # MINIMUM VIABLE: JUST A LABEL SAYING THE CURRENT STEP
        step_label_label = tk.Label(self.frame0, text='Step: ')
        self.step_label = tk.Label(self.frame0, textvariable=self.step_var)
        step_label_label.pack(side=tk.LEFT)
        self.step_label.pack(side=tk.LEFT)

    def poll_queue(self):
        try:
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                print(result)
                self.step_var.set(result)
        except Exception as e:
            print(f"Error reading from queue: {e}")
        finally:
            self.parent.after(100, self.poll_queue)

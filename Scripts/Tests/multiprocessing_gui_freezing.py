import threading # create processpool on separate thread so main thread can focus on GUI
from concurrent.futures import ProcessPoolExecutor #multiprocessing
import tkinter as tk
import time
import numpy as np
from multiprocessing import Queue, Manager

"""
Tests the capability of tkinter window to work alongside a multiprocessing function.
"""
class app():
    def __init__(self):
        self.result_queue = Queue()

        self.root = tk.Tk()
        self.var = tk.IntVar()
        # widgets
        ## Frames
        self.main_frame = tk.Frame(self.root)
        ## Contents
        self.button = tk.Button(self.main_frame, text="Run Process")
        self.label = tk.Label(self.main_frame, text="", textvariable=self.var)

        # packing
        self.main_frame.pack()
        self.button.pack()
        self.label.pack()

        # configuring
        self.button.configure(command=self.processed_method)

        # polling
        self.poll_queue()

    def poll_queue(self):
        try:
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                self.var.set(result)
        except Exception as e:
            print(f"Error reading from queue: {e}")
        finally:
            self.root.after(100, self.poll_queue)

    def run_app(self):
        self.root.mainloop()

    """
    Creates a new thread, then creates a processpool on that separate thread for a task.
    """
    def processed_method(self, **kwargs):
        process_thread = threading.Thread(target=start_process, args=(self.result_queue,), daemon=True)
        process_thread.start()

"""
emulates a long task that would be multiprocessed.
"""

def long_task(n):
    time.sleep(1)
    print(n)

    return n

def start_process(queue):
    long_arr = np.arange(1000)
    with ProcessPoolExecutor() as executor:
        futures = executor.map(long_task, long_arr)
        for future in futures:
            queue.put(future)

if __name__ == "__main__":
    app = app()
    app.run_app()


"""
Group of widgets that control certain behaviors for output files.
"""
import tkinter as tk
from files.create import default_output_file_name, default_output_file_dir

"""
You click the calculate button, and this pops up.
"""
class output_popup(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.out_name = tk.StringVar()
        # as this widget is created after some events, this global var should be populated.
        self.out_name.set(default_output_file_name) # initialize the tk stringvar with the value.

        self.title("Output File Params")
        self.description = tk.Label(text="Check it out")

        self.text1 = tk.Label(text="Output Folder Location: ")
        self.text2 = tk.Label(text="Output Name: ")

        self.text3 = tk.Label(text=default_output_file_dir)
        self.entry2 = tk.Entry(textvariable=self.out_name)

            # PACKING
        self.description.grid(row=0, column=0)

        self.text1.grid(row=1, column=0)
        self.text3.grid(row=1, column=1)

        self.text2.grid(row=2, column=0)
        self.entry2.grid(row=2, column=1)
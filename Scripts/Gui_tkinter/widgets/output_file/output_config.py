
"""
Group of widgets that control certain behaviors for output files.
"""
import tkinter as tk
from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import manager_1, m1f1

"""
You click the calculate button, and this pops up.
"""
class output_popup(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.out_name = tk.StringVar()

        self.title("Output File Params")
        self.description = tk.Label(text="Check it out")

        self.text1 = tk.Label(text="Output Folder Location: ")
        self.text2 = tk.Label(text="Output Name: ")

        self.entry = tk.Entry(textvariable=self.out_name)


"""
Group of widgets that control certain behaviors for output files.
"""
import tkinter as tk
from files.create import default_output_file_name, default_output_file_dir
from system.temp_file_names import param_keys, m1f1
from system.temp_manager import TEMPMANAGER_MANAGER, update_temp, read_temp_file_dict

"""
You click the calculate button, and this pops up.
"""
class output_popup(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
            # instance attributes (these are saved to the tempfile at its end)
        self.out_name = tk.StringVar()
        self.output_path:str = default_output_file_dir
            # as this widget is created after some events, this global var should be populated.
        self.out_name.set(default_output_file_name) # initialize the tk stringvar with the value.

            # WIDGETS
        self.title("Output File Params")
        self.description = tk.Label(text="Check it out")

        self.text1 = tk.Label(text="Output Folder: ")
        self.text2 = tk.Label(text="Output Name: ")
            # content labels and entries
        self.file_button = tk.Button(master, text="Browse", command=self.file_button_clicked)
        self._text3 = tk.Label(text=self.output_path)
        self.entry2 = tk.Entry(textvariable=self.out_name)

            # PACKING
        self.description.grid(row=0, column=0)

        self.text1.grid(row=1, column=0)
        self._text3.grid(row=1, column=1)
        self.file_button.grid(row=1, column=2)
        #self.text3.grid(row=1, column=2)

        self.text2.grid(row=2, column=0)
        self.entry2.grid(row=2, column=1)

    """
    When the 'browse' button is clicked, this pops up the file explorer.
    Note that there is a known default directory.
    """
    def file_button_clicked(self, event=None, *args):
            # open a directory browser open to the currently configured dir.
        _output_path = tk.filedialog.askdirectory(title='Select Location for Output Folder', initialdir=self.output_path)
            # update the currently configured dir and the text labelling it
        if _output_path:
            self.output_path = _output_path
            self._text3.config(text=self.output_path)


    """
    Before closing this window, make sure to store the location to place these things.
    I choose to collect this info at the end (and not every single time the values are edited) because
    the user loop for this widget is entirely self-contained and brief.
    """
    def on_close(self, event=None, *args):
        d = {}
        d[param_keys.output_location.name] = self.output_path
        d[param_keys.output_name.name] = self.out_name.get()
        update_temp(TEMPMANAGER_MANAGER.files[m1f1], d)
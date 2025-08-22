
"""
Group of widgets that control certain behaviors for output files.
"""
import tkinter as tk
from files.create import default_output_file_name, default_output_file_dir, get_output_name, get_default_output_dir
#from system.temp_file_names import param_keys, m1f1
#from system.temp_manager import TEMPMANAGER_MANAGER, update_temp, read_temp_file_dict
from system.state_dict_main import AppConfig
import os
import numpy as np
from pandas import read_csv

"""
You click the calculate button, and this pops up.
"""
class output_popup(tk.Toplevel):
    def __init__(self, master, close_callable:callable=None, params:AppConfig=None,  *args, **kwargs):
        super().__init__(master, **kwargs)
        self.params = params
        self.attributes("-topmost", True)
        self.close_callable = close_callable
            # instance attributes (these are saved to the tempfile at its end)
        self.out_name = tk.StringVar()
        self.output_path:str = get_default_output_dir(params)
            # as this widget is created after some events, this global var should be populated.
        self.out_name.set(get_output_name(self.output_path, self.params)) # initialize the tk stringvar with the value.

            # FRAMES - for aligning content
        self.header_frame = tk.Frame(self)
        self.body_frame = tk.Frame(self)
        self.footer_frame = tk.Frame(self)

            # WIDGETS - functionality
        self.title("Output File Params")
        self.description = tk.Label(text="Check it out", master=self.header_frame)
        self.text1 = tk.Label(text="Output Folder: ", master=self.body_frame)
        self.text2 = tk.Label(text="Output Name: ", master=self.body_frame)
            # content labels and entries
        self.file_button = tk.Button(master=self.body_frame, text="Browse", command=self.file_button_clicked)
        self._text3 = tk.Label(text=self.output_path, master=self.body_frame)
        self.entry2 = tk.Entry(textvariable=self.out_name, master=self.body_frame)
            # ship it button on the bottom
        self.confirm_button = tk.Button(self.footer_frame, text="Ship It", command=self._close)

            # CONFIGURE - need to make sure that on the highest level, column 0 takes up entire length
        self.columnconfigure(0, weight=1)

            # PACKING
                # organizational frames
        self.header_frame.grid(row=0, column=0)
        self.body_frame.grid(row=1, column=0)
        self.footer_frame.grid(row=2, column=0)

                # header content
        self.description.grid(row=0, column=0)
                # body content
        self.text1.grid(row=0, column=0)
        self._text3.grid(row=0, column=1)
        self.file_button.grid(row=0, column=2)
        #self.text3.grid(row=1, column=2)
        self.text2.grid(row=1, column=0)
        self.entry2.grid(row=1, column=1)
                # footer content
        self.confirm_button.grid(row=0, column=1)

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
            self.out_name.set(get_output_name(self.output_path, self.params))


    """
    Before closing this window, make sure to store the location to place these things.
    I choose to collect this info at the end (and not every single time the values are edited) because
    the user loop for this widget is entirely self-contained and brief.
    """
    def _close(self, event=None, *args):
            # update the tempfile with the path and name information
        d = {}
        self.params.path.output_absolute = self.output_path
        self.params.path.output_name = self.out_name.get()
        self.params.path.output = os.path.join(self.output_path, self.out_name.get())
        self.params.particle.dataframe = read_csv(self.params.path.particle, dtype=np.float64)
            # call the closing callable (provided on initialization)
        if self.close_callable is not None:
                self.close_callable()
            # delete self
        self.destroy()

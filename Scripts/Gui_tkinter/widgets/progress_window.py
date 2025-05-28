import tkinter as tk
from tkinter import ttk
from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import manager_1, m1f1
from Gui_tkinter.widgets.menu.text_styles import GUI_Label
from settings.palettes import GUI_Fonts
from files.create import get_unique_coil_collection_amps

"""
a pop-up window created right after the 'calculate' button is pressed.
keeps track of simulation progress.
"""
class calculate_progress_window(tk.Toplevel):
    def __init__(self, parent: tk.Tk, queue):
        tk.Toplevel.__init__(self, parent)
            # multiprocessing manager
        self.result_queue = queue
        self.step_var = tk.StringVar()
            # window geometry
        self.parent = parent
        self.geometry("1000x600")

            # window internals
        self.live = live_info(self, self.step_var)
        self.separator = ttk.Separator(self, orient='vertical')
        self.summary = param_summary(self)

            # packing
        self.live.pack(side=tk.LEFT, expand=True, fill="y")
        self.separator.pack(side=tk.LEFT, expand=True, fill="y")
        self.summary.pack(side=tk.LEFT, expand=True, fill="y")




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

"""
the rightside section of the progress window, holds a summary of the parameters in use.
"""
class param_summary(tk.Frame):
    def __init__(self, master, **kwargs):
            # Initialize pre-GUI info
        super().__init__(master, **kwargs)
        self.params = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
        self.fonts = GUI_Fonts(self)

            # GUI stuff
        self._init_Widgets()
    
    """
    place for all the widgets, placement and creation etc etc
    """
    def _init_Widgets(self):
            # title: SUMMARY
        title = GUI_Label(self, self.fonts['title'], "Summary")

            # heading 1: coil info
        coil_info_frame = tk.LabelFrame(self, text="Coil Info")
                # info leaders
        _coil_name = tk.Label(coil_info_frame, text="File Name: ")
        _coil_amp = tk.Label(coil_info_frame, text="Amp (T):")
        _coil_position = tk.Label(coil_info_frame, text="Offset (M)")
                # actual info
        coil_name = tk.Label(coil_info_frame, text=self.params["coil_file"])
        coil_amp = tk.Label(coil_info_frame, text=get_unique_coil_collection_amps(self.params['mag_coil']))
        coil_position = tk.Label(coil_info_frame, text=str(abs(self.params['mag_coil'].children[0].position[0])))

            # PACKING
        title.grid(row=0, column=0)
        coil_info_frame.grid(row=1, column=0)

        _coil_name.grid(row=0, column=0)
        coil_name.grid(row=0, column=1)
        _coil_amp.grid(row=1, column=0)
        coil_amp.grid(row=1, column=1)
        _coil_position.grid(row=2, column=0)
        coil_position.grid(row=2, column=2)

"""
the leftside of the popup window, contains updating information from the calculation.
"""     
class live_info(tk.Frame):
    def __init__(self, master, step_var, **kwargs):
        self.master = master
        super().__init__(master, **kwargs)

        ###########################################################
            # MINIMUM VIABLE: JUST A LABEL SAYING THE CURRENT STEP
        self.step_var = step_var

        step_label_label = tk.Label(self.master, text='Step: ')
        self.step_label = tk.Label(self.master, textvariable=self.step_var)
        step_label_label.pack(side=tk.LEFT)
        self.step_label.pack(side=tk.LEFT)

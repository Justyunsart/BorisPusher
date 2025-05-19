import tkinter as tk
from Gui_tkinter.funcs.GuiEntryHelpers import FileDropdown


"""
widget that contains a button next to a tk.Combobox.
The widget's button component expects something to update (toggle visibility for context menu)

# Parameters
master (tk.Frame or similar) : the tkinter object that contains this widget.
"""
class Param_Button_and_Dropdown(tk.Frame):
    def __init__(self, master, param_name="Param", dir:str=None, default:callable=None, context_widget=None, **kwargs):
        self.master = master
        self.param_name = param_name
        
        super().__init__(master=master, **kwargs)

        #####################################s
        # widget things
            # Instantiate the constitutient widgets
        self.button = tk.Button(master=self, text=self.param_name)
        self.dropdown = FileDropdown(master=self, state='readonly', dir=dir, default=default)
            # packing
        self.button.grid(row=0, column=0, padx=5, pady=2)
        self.dropdown.grid(row=0, column=1, padx=5, pady=2)

"""
Class for context menu widgets: must contain method for toggling them on and off.
"""
class context_widget(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.InitWidget()
    """
    When implementing, place all the widgets here
    """
    def InitWidget(self):
        pass
    """
    When called, toggles the visiblity of all its widgets on.
    """
    def ShowWidget(self):
        pass
    """
    When called, turns all its widgets invisible.
    """
    def HideWidget(self):
        pass


"""
The object that spawns and despawns related widgets based on a button press in the Param_Button_and_Dropdown object.
"""
class ParamContextMenu(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.instances = []

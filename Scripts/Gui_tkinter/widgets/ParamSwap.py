
"""
New GUI structure, starting fresh on a new script.
You can imagine this class as the main content of the calc tab.
"""

import tkinter as tk
from Gui_tkinter.widgets.ScrollableFrame import ScrollableFrame
from Gui_tkinter.widgets.Param_name_n_dropdown import Param_Button_and_Dropdown

class ParamSwap(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.buttons = [] # tracker for the functionality of making only one button be pressed at a time

        ###################################################
            # Main organizational frames: 
                # Bottom horizonal fill frame for the calculate button
                # Two frames fill the rest of the space (left shows params, right shows context menu)
        self.frame_bottom = tk.Frame(self)
        self.frame_params = tk.Frame(self)
        self.frame_context = tk.Frame(self)

            # Configure frame size weights
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0, minsize=30, pad=5)
        #self.columnconfigure(0, weight=0.5, pad=5)
        #self.columnconfigure(1, weight=0.5, pad=5)

            # Packing
        self.frame_bottom.grid(row=1, column=0, columnspan=2, sticky=tk.S, padx=5, pady=5)
        self.frame_params.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.frame_context.grid(row=0, column=1, sticky=tk.E, padx=5, pady=2)

        ###################################################
        # Actually put things inside the empty frames
            # Calculate callback button
        self.ship_it = tk.Button(self.frame_bottom, text="Ship it")
            # Parameter frame(left side)
        self.scrollable_params = ScrollableFrame(self.frame_params)
        self._init_param_dropdowns()

            # Packing
        self.ship_it.grid(row=0, column=0)
        self.scrollable_params.grid(row=0, column=0)

        ###################################################
        # Things to run at the very end (when all widgets have been created)
        self.scrollable_params.RegisterScrollArea()

    """
    This function controls all the widgets that show up in self.scrollasble_params.
    """
    def _init_param_dropdowns(self):
        def create_param_widget(master, param_name, dir, default:callable, widget):
            param =  Param_Button_and_Dropdown(master=master, param_name=param_name, dir=dir, default=default, context_widget=widget)
            self.buttons.append(param.button)
            param.button.configure()
    
    """
    1st, make sure the pressed button gets stuck in the pressed state.
    2nd, release all other pressed buttons (if any). Ideally, only one should be pressed at a time.
    3rd, hide the currently displayed context widget
    4th, show the widget belonging to the object with the pressed button.
    """
    def _button_callback(self, event):
        pass

if __name__ == "__main__":
    from debug.empty_app import create_empty_tk

    root, mainframe = create_empty_tk()

    wid = ParamSwap(mainframe)
    wid.pack()
    root.mainloop()
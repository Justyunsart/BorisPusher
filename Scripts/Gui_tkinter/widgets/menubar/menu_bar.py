import tkinter as tk
from functools import partial
from Gui_tkinter.widgets.menubar.settings import SettingsWindow

"""
Parent class containing all the menu bar items.
"""

class borisMenu():
    def __init__(self, root:tk.Tk):
        self.root = root
        root_menubar = tk.Menu(self.root)


        ############################################################
            # File cascade
        file = tk.Menu(root_menubar, tearoff=False)
        root_menubar.add_cascade(label='File', menu = file)
        file.add_command(label='Settings', command=partial(SettingsWindow, self.root))
        file.add_separator()
        file.add_command(label='Exit', command=self.root.destroy)


        self.root.config(menu=root_menubar)

if __name__ == '__main__':
    root = tk.Tk()
    menubar = borisMenu(root)
    root.mainloop()
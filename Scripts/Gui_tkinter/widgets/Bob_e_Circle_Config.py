"""
A tk.Toplevel object that opens on a button press.
This window will contain the ability to control the circles that are used in the Bob_e method.

Even though they are not going to be used for field calculations and stuff, I'm still going to use
magpylib's circle object for this because graphing and rotation is easy.
"""
from Gui_tkinter.widgets.CurrentGuiClasses import CurrentEntryTable
from Gui_tkinter.funcs.GuiEntryHelpers import Bob_e_Config_Dataclass
import tkinter as tk
from system.path import Path
from system.temp_file_names import param_keys

# NOTE: For this class to work, the class will need a reference to the tk root.
# Because the GUI mainloop is encapsulated in a function, it cannot be done as an import.
# That is why this window is going to exist as a class.

class Bob_e_Circle_Config(tk.Frame):
    """
    (param: ) root: the base tk.Tk object for the tkinter app.
    """
    def __init__(self, root:tk.Tk, dir, **kwargs):
        self.root = root
        super().__init__(root, **kwargs)

        # Main frame container for the toplevel's new window
        self.main_frame = tk.Frame(self)
        self.table_frame = tk.Frame(self.main_frame)
        self.graph_frame = tk.Frame(self.main_frame)

        self.dir = Path(dir, "bob_e")
        # widgets here
        self.entry_table = CurrentEntryTable(master=self.table_frame,
                                            dataclass=Bob_e_Config_Dataclass,
                                            graphFrame=self.graph_frame,
                                            DIR=self.dir,
                                            collection_key=param_keys.bob_e_coil.name, 
                                            path_key=param_keys.bob_e_file.name, 
                                            name_key=param_keys.bob_e_name.name,)

        # packing step
        self.main_frame.pack(fill='both', expand=1)
        self.table_frame.pack(side='right', expand=1)
        self.graph_frame.pack(side='left')
    def get_collection(self):
        """
        returns the CurrentEntryTable's magpylib.Collections object.
            > Conveniently holds information for us.
        """
        return self.entry_table.collection
    

if __name__ == "__main__":
    from pathlib import Path
    import os
    """
    Create a tk object w/ entry tables to test thingies.
    """
    # application root
    root = tk.Tk()

    # main window
    root_frame = tk.Frame(root)


    # get DIRs
    path_root = str(Path(__file__).resolve().parents[1]) #Expected: '/BorisPusher/...'
    path_defaults = os.path.join(path_root, f"Inputs/Bob_E Configurations/Defaults")
    path_DIR = os.path.join(path_root, f"Inputs/Bob_E Configurations")

    # TEST WIDGETS STARTING HERE
    test_table = Bob_e_Circle_Config(root=root, defaults=path_defaults, dir=path_DIR)
    
    
    # packing
    root_frame.pack(expand=1, fill='both', anchor='center')
    test_table.pack()

    root.mainloop()


if __name__ == "__main__":
    """
    Testing the usage of a factory pattern for automation of data-to-UI widget class creation
    """
    from Gui_tkinter.funcs.GuiEntryHelpers import (SolverUi, Solver_Ring_Data, Solver_Washer_Data)
    import tkinter as tk

    # Create example preset
    row = Solver_Ring_Data(PosX=0, PosY=0, PosZ=1.1, Diameter=0.75, Current=10000)

    # Create blank row just so that the UI class can be made
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()

    ui_data = SolverUi(frame, row)

    print(row)
    print(ui_data)
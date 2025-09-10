
"""
test the functionality of layout classes.
"""

if __name__ == "__main__":
    import tkinter as tk
    from Gui_tkinter.widgets.layout import (JustifyLeft, JustifyRight, JustifyCenter, JustifyNull, LayoutFrame)

    # Create blank app
    root = tk.Tk()
    root.geometry('800x400')

    # Create parent frame
    mainframe = LayoutFrame(root, JustifyLeft)

    # Create children widgets to add to mainframe
    mainframe.add(tk.Label(text="LOL"))
    mainframe.add(tk.Label(text="LOL2"))
    mainframe.add(tk.Label(text="LOL3"))

    # Packing
    # Only for the mainframe, as the widgets it has control over are supposed to be auto-placed.
    mainframe.pack(fill='both', expand=True)

    root.mainloop()
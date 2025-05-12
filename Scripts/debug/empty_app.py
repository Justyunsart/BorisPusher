import tkinter as tk

"""
definition for an empty tkinter application. Used as a shortcut for creating these things
for testing.
"""
def create_empty_tk():
    # base application
    root = tk.Tk()

    # main frame
    mainframe = tk.Frame(root)

    # packing
    mainframe.pack()

    return root, mainframe

"""
Creates a window with a button.
"""
def create_button_tk():
    root, mainframe = create_empty_tk()

    # create the testing button
    button = tk.Button(mainframe, text="Press me")

    # packing
    button.pack()

    return root, mainframe, button
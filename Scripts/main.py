"""
Script to run the GUI mainloop; run this to start the program.
"""
"""
# PLOTTING SCREEN
Plotting logic is all contained in Scripts/PlottingWindow.py.
The PlottingWindowObj class has all the graphs present in the plotting window, which is:
    > a larger 3D graph to show trajectory
    > two 2D graphs with a dropdown menu for the choice of data to visualize.

## GRAPHING ALGEBRA
While the trajectory graph is just a 3D scatterplot of all the positional data, the 2D graphs involve
some math.

The dropdown graphs use the function 'Param_v_Step_callable', in which:
    > If the selected dropdown is the b field, it just plots the b field magnitudes in a line graph
    > If the v or e options are selected, it plots:
        1. The magnitudes at each step
        2. The magnitude of the cross product with b
        3. The dot products with b

"""
from Gui_tkinter.BorisGui import OpenGUI

if __name__ == "__main__":
    # For whatever reason, instantiating the GUI window HAS to 
    # be encapsulated in a function.

    # If I call root.mainloop() here, it gets called when a process
    # spawns, even when inside the main block. 
    OpenGUI()
    
    
"""
packages:
"""
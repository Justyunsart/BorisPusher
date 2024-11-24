# RUN THIS TO RUN THE PROGRAM LOL

from BorisGui import OpenGUI

if __name__ == "__main__":
    # For whatever reason, instantiating the GUI window HAS to 
    # be encapsulated in a function.

    # If I call root.mainloop() here, it gets called when a process
    # spawns, even when inside the main block. 
    OpenGUI()
    
    """
    num_parts = df.shape[0]
    num_points = entry_numsteps_value.get()

    dt = entry_sim_time_value.get()/num_points

    if(isRun.get()):
        magpy4c1.runsim(df, num_parts, num_points,dt, entry_sim_time_value.get())
        
    """
          
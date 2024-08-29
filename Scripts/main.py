# RUN THIS TO RUN THE PROGRAM LOL

from BorisGui import root, isRun, inpd, do_file, entry_numsteps_value, time_step_value, entry_sim_time_value
import magpy4c1
import pandas as pd
from PusherClasses import InitializeData

if __name__ == "__main__":
    root.mainloop()
    
    df = InitializeData(do_file.get(), inpd.get())
    num_parts = df.shape[0]
    num_points = entry_numsteps_value.get()

    dt = entry_sim_time_value.get()/num_points

    if(isRun.get()):
        magpy4c1.runsim(df, num_parts, num_points,dt, entry_sim_time_value.get())
        
    
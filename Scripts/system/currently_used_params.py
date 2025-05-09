
"""
The new central location for all relevant simulation parameters that the current simulation is running.

ORDER OF EVENTS:
1. The GUI supplies information here when the calculate button is pressed.
2. The calculation script (magpy4c1.py) references the info from this script when running.

"""
data = {} # global var to contain the params when GatherParams() is called.


'''
Obtains the current values of all supplied parameters.
It is expected that every widget in the params list contains a GetData() function that
returns a parsable dictionary; this function merges all the dicts to a superdict.

This function updates the global data var so that other scripts can access it.

PARAMS:
params: the list that keeps a reference to all relevant tkinter objects.
'''
def GatherParams(params:list):
    global data
    for widget in params:
        x = widget.GetData()
        #print("x is: ", x)
        data = {**data, **x} # merge the resulting dictionaries to update the original data container
        #print("data updated to: ", data)
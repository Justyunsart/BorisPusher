
"""
Field solvers each have metadata associated with them like:
    - name of each column (representing parts of a coil)
    - the type of data (and tkinter widget) associated with each column
    - methods to format/gather its information to a nested dict. or another expected format

These classes should:
    - never enforce any default values, as that's the job of presets
    - only track column names, type, and widgets, and any helpers associated with retrieval
    - represent a row of a data table when initialized
"""


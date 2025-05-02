from files.checks import folder_checks
"""
Extra logic to run on application startup.
These include:
    - Inputs folder checks
"""
def on_start():
    folder_checks() # ensure that all configured dirs exist and are legal.
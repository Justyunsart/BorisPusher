import configparser
import os


"""
Needed because of how user configs work. They exist separately, but with the same structure.
Config will read both, taking the user config info over the default's.

It is expected that the user configs file only stores deviations from the default values.
"""
runtime_configs = configparser.ConfigParser()
def read_configs():
    global runtime_configs
    cwd = os.getcwd()
    path = f"{cwd}/Scripts/settings/configs"
    
    if os.path.exists(f"{path}/usr_configs.ini"):
        runtime_configs.read([f"{path}/default_configs.ini", f"{path}/usr_configs.ini"])
    else:
            runtime_configs.read(f"{path}/default_configs.ini")
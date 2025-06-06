import configparser
import os
from definitions import DIR_ROOT


"""
Needed because of how user configs work. They exist separately, but with the same structure.
Config will read both, taking the user config info over the default's.

It is expected that the user configs file only stores deviations from the default values.
"""
runtime_configs = configparser.ConfigParser()
def read_configs():
    global runtime_configs
    path = os.path.normpath(f"{DIR_ROOT}/Scripts/settings/configs")
    
    if os.path.exists(os.path.normpath(f"{path}/usr_configs.ini")):
        runtime_configs.read([os.path.normpath(f"{path}/default_configs.ini"), os.path.normpath(f"{path}/usr_configs.ini")])
    else:
        runtime_configs.read(os.path.normpath(f"{path}/default_configs.ini"))
    #print(os.path.normpath(f"{path}/default_configs.ini"))
    #print(runtime_configs.sections())

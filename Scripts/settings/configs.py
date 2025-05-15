import configparser
from definitions import DIR_ROOT, NAME_INPUTS, PLATFORM
import os

"""
Run only to create new .ini files when it does not yet exist.
manager for the config .ini file that dictates the values
that are populated in definitions.py
"""

def create_config():
    config = configparser.ConfigParser()
    config['System'] = {'Platform': PLATFORM}
    config['Paths'] = {'Inputs' : os.path.join(DIR_ROOT, str(NAME_INPUTS)),}

    with open(os.path.join(DIR_ROOT, 'config.ini'), 'w') as f:
        config.write(f)


import configparser
from definitions import NAME_DEF_CONFIG, NAME_USR_CONFIG, DIR_ROOT
import os
from files.windows.get_documents_path_win import get_documents_path_win



def create_default_config():
        # CONFIGURE THE ACTUAL INI FILE
    config = configparser.ConfigParser()
    config['Paths'] = {
        'usr_Documents' : os.path.normpath(os.path.join(os.path.expanduser('~/Documents'), "Boris_Usr"))
        if os.path.exists(os.path.normpath(os.path.expanduser('~/Documents')))
        else os.path.normpath(os.path.join(get_documents_path_win(), "Boris_Usr")),
        'Inputs' : "%(usr_Documents)s/Inputs",
        'Outputs' : "%(usr_Documents)s/Outputs",
    }
        # SAVE TO A FILE.
    path = os.path.normpath(f"{DIR_ROOT}/Scripts/settings/configs")
    with open(os.path.join(path, NAME_DEF_CONFIG), 'w+') as f:
        config.write(f)



'''
"""
Create a config.ini file with defaults!

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

'''

def read_config():
    cwd = os.getcwd()
    path = f"{cwd}\\Scripts\\settings\\configs"
    config = configparser.ConfigParser()
    config.read(f"{path}\\default_configs.ini")
    print(config["Paths"]['inputs'])

if __name__ == "__main__":
    # create the default config settings object.
    create_default_config()
    #read_config()
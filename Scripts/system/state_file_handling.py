
"""
Configuration/state files should be stored in different places depending on the OS
    - Windows = AppData/Local
    - macOS = Application Support/
    - Linux = ./config/

For this program, state files could include stuff like:
    - the last-used AppConfig dataclass
"""
from definitions import app_name, roaming
from appdirs import user_data_dir
import os

def get_config_dir():
    """
    Get the path where parameter binaries should be stored.
    Different for different os, so that's whey we use the appdirs package
    """
    config_folder_name = "Config"
    _dir = user_data_dir(app_name,
                        appauthor=False,
                        version=None,
                        roaming=roaming)
    return os.path.join(_dir, config_folder_name)

def get_log_dir():
    """
    This will be the location where any debug logs are sent to.
    """
    log_dir_name = "Log"
    _dir = user_data_dir(app_name,
                         appauthor=False,
                         version=None,
                         roaming=roaming)
    return os.path.join(_dir, log_dir_name)




if __name__ == "__main__":
    dir = user_data_dir(app_name,
                        appauthor=False,
                        version=None,
                        roaming=roaming)

    print(dir)
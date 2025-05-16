from definitions import DIR_ROOT
import os
from Scripts.system.temp_manager import read_temp_file_dict


if __name__ == "__main__":
    dct = read_temp_file_dict(os.path.join(DIR_ROOT, "last_used"))

"""
When something needs to be logged to a file, these functions help set up the logger to write to
"""

import logging
import os
from system.state_file_handling import get_log_dir

def setup_logger(logfile="new.log", level=logging.DEBUG):
    # Debug log dir. is set by os. get it and make sure it exists
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, logfile), mode='w', encoding="utf-8"),  # log to file
            logging.StreamHandler()  # also log to console
        ]
    )
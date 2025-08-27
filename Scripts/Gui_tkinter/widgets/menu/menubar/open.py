
"""
Helper functions for the menubar's Open... menu
where it creates/travels to configured dirs.

Needs to be platform-independent
"""
import os
from pathlib import Path
import subprocess
from definitions import PLATFORM

def open_dir(path: str):
    """Open system file explorer at given path, creating it if missing."""
    dir_path = Path(path).expanduser().resolve()
    os.makedirs(dir_path, exist_ok=True)  # create if it doesn't exist

    if PLATFORM.startswith("win"):
        subprocess.run(["explorer", str(dir_path)])
    elif PLATFORM == "darwin":  # macOS
        subprocess.run(["open", str(dir_path)])
    else:  # assume Linux / other Unix
        subprocess.run(["xdg-open", str(dir_path)])
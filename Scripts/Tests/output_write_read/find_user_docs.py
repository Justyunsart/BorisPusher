
"""
Find the user's documents folder
"""

from pathlib import Path
import os

def print_home_dir():
    home = Path.home()
    print(home)


if __name__ == '__main__':
    print(os.path.normpath(os.path.expanduser('~/Documents')))
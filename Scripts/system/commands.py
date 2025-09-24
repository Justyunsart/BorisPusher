import shutil
from abc import ABC, abstractmethod
import csv

# HEADER
class Command(ABC):
    """base class for commands that can touch os stuff, which can be called from multiple senders"""
    @abstractmethod
    def execute(self):
        pass

# IMPLEMENTATIONS
class SaveDictCsv(Command):
    """Provided a dictionary with variable_name:every_row_value, saves as a csv to the desired path"""
    def __init__(self, data, destination):
        self.data = data
        self.destination = destination

    def execute(self):
        columns = list(self.data.keys())
        rows = zip(*self.data.values())

        with open(self.destination, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns) #header
            writer.writerows(rows) #rows

class CopyFile(Command):
    """Wrapper so that scheduling this command with the command bus is with the same structure"""
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
    def execute(self):
        shutil.copyfile(self.source, self.destination)

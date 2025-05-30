from tempfile import NamedTemporaryFile
import weakref
import os
import shutil
from definitions import DIR_ROOT
from Scripts.system.temp_file_names import m1f1
from functools import reduce

"""
Manages all the manager instances
"""
class TempManager_Manager():
    def __init__(self):
        #print(f"manager init")
        # A WeakValueDictionary makes it so that TempManagers not referenced anywhere else will make it be garbage collected
        self.managers = weakref.WeakValueDictionary() # Key = manager name, Value = manager ref
        self.files = {} # Key = file name, Value = file ref
        self.imgs = []

    """
    Runs a check whether the given weakref has been garbage collected yet.
    """
    def isActive(self, manager) -> bool:
        if manager() is not None:
            return True
        return False
    
    """
    creates a new TempManager instance and adds it to self.managers.
    Since the Event class is essentially a list of callables (expected to run w/ no args),
    this function just appends the newly created TempManager's deconstruction method to it.

    PARAMETERS
    name: internal label to refer to the manager instance.
    closing_event: When it is None, defualts to when the program terminates.
    """
    def add_temp_manager(self, name:str):

        new_man = TempManager(master=weakref.proxy(self)) # create new manager
        self.managers[name] = new_man # add the object to self.managers

        # just in case, make the child manager delete its temp files when it is garbage collected.
        # should theoretically never run but it's for peace of mind.
        weakref.finalize(new_man, new_man.delete_all_files)
    
    """
    Deletes a TempManager child object by name if an entry exists in self.managers
    """
    def del_temp_manager(self, name:str):
        manager:TempManager
        manager = self.managers[name]
        if self.isActive(manager):
            manager().delete_all_files()

    """
    Called when the program terminates; tells all of its children to run its
    deconstructor.
    """
    def del_all_temp(self):
        manager:TempManager
        for manager in self.managers.valuerefs():
            if self.isActive(manager):
                manager().delete_all_files()
        for img in self.imgs:
            if os.path.exists(img):
                os.remove(img)

    """
    Attempts to tell its child TempManager instance to create a new file.
    """
    def create_temp_file(self, m_name, f_name):
        manager:TempManager
        manager = self.managers.get(m_name)
        manager.add_tempfile(f_name)

    """
    Runs before the program closes. 
    Before deleting all tempfiles, dump the one holding all params somewhere into the program.
    """
    def dump_params(self):
        dst = os.path.join(DIR_ROOT, 'last_used')
        shutil.copyfile(src=self.files[m1f1], dst=dst)

    """
    Run from child; happens when a new file is made
    """
    def child_update(self, page, name):
        # add a weakref to the file inside self.files
        self.files[name] = page

"""
Constructs the main manager manager.
"""
TEMPMANAGER_MANAGER = TempManager_Manager()

"""
Responsible for keeping temp file/folder references.

PARAMS
master(TempManager_Manager): the manager's manager.
"""
class TempManager():
    def __init__(self, master):
        self.files = {}
        self.tmps = {}
        self.master = master
    
    """
    When called, the TempManager instance closes all of its associated tempfiles
    """
    def delete_all_files(self):
        # call the close function on all stored file values.
        for file in list(self.tmps.values()):
            file.close()
            os.remove(file.name)
        # reset the self.files dict
        self.tmps = {}
        
        #print(f"all temp files deleted!")

    """
    Adds a new file to the self.files dict.
    Expects a name. It will be used as both as the tempfile function's prefix, as well
    as the self.files dict entry's key.
    """
    def add_tempfile(self, name:str):
        tmp = NamedTemporaryFile(prefix=name, mode='wb', delete=False)
        pickle.dump({}, tmp) # start w empty dict
        self.files[name] = tmp.name
        self.tmps[name] = tmp
        
        # add to your manager's flattened pages list.
        self.master.child_update(tmp.name, name)

################################
# HELPERS FOR EXTERNAL SCRIPTS #
################################
import pickle

"""
Either return the decoded dictionary from the tempfile
or return an empty one if it can't decode.
"""
def read_temp_file_dict(path):
    debug = False
    with open(path, 'rb') as f:
        try:
            if debug:
                d = pickle.load(f)
                print(f"system.temp_manager.read_temp_file_dict(): json read as: ")
                print(d)
                return d
            else:
                return pickle.load(f)
        except:
            #print(f"exception when reading temp file, returning empty")
            return {}
        
"""
Write to tempfile path
"""
def write_dict_to_temp(path, data):
    debug = False
    if debug:
        print(f"system.temp_manager.write_dict_to_temp(): data is: ")
        print(data)
    with open(path, 'wb') as f:
        pickle.dump(data, f)

def update_temp(temp, update, nested=False, key=None):
    d = read_temp_file_dict(temp)
    if not nested:
        d.update(update)
    else:

        #The function accepts a list of keys for deeper nests.
        if type(key) == list:
            _d = d
            for k in key:
                if k not in _d:
                    _d[k] = {}
                _d = _d[k]
            _val = reduce(dict.__getitem__, key, d)
            _val.update(update)
            print(_val)

        #If 'key' is not a list, it is assumed to be at a nest depth of 1.
        else:
            if key not in d:
                d[key] = {}
            d[key].update(update)
    write_dict_to_temp(temp, d)
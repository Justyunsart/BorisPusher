"""
container for the observer pattern: for flagging events and triggering updates.
"""
class Observed:
    '''
    A value that is being watched for any changes.
    
    
    Event subscribers will run their update function
    upon being notified.
    '''
    def __init__ (self):
        self._observers = []
    
    def notify (self, modifier = None):
        '''
        Run update function in observers
        '''
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)
    
    def attach(self, observer):
        '''
        Add observer to list if not in list already
        '''
        if observer not in self._observers:
            self._observers.append(observer)
        
    def detach(self, observer):
        '''
        if in list, remove observer
        '''
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

class Data(Observed):
    '''
    thing that is being observed, with initilizer data and such
    '''
    def __init__ (self, name=''):
        Observed.__init__(self)
        self.name = name
        self._data = 0
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value
        self.notify()

"""
Controller for when commands are executed.
"""

class CommandBus:
    def __init__(self):
        self.handlers = {} #Tracker for the currently registered event key:function

    def register(self, event_handle,command):
        """Store event name + command to run into self.handlers"""
        self.handlers[event_handle] = command

    def dispatch(self, event_handle, command=None):
        func = self.handlers.get(event_handle)
        if not func:
            raise ValueError(f"No func registered for event {event_handle}")
        if command is not None:
            return func(command)
        return func()
from abc import ABC, abstractmethod

class Listener(ABC):
    EVENT_CREATE = 0
    EVENT_UPDATE = 1
    EVENT_DELETE = 2
    
    @abstractmethod
    def receive_evt(self, img, track, evt_type):
        pass
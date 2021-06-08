from abc import ABC, abstractmethod


class Packable(ABC):
    """Abstract class representing an object whose project can be parsed into a dict"""

    @abstractmethod
    def pack(self):
        pass

    @abstractmethod
    def unpack(self, data):
        pass

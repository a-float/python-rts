from abc import ABC, abstractmethod


class Receiver(ABC):
    """Abstract class representing an object which can receive data from a client"""

    @abstractmethod
    def handle_message(self, message):
        pass

from abc import ABC, abstractmethod

class DomainClassInterface(ABC):
    """
    An abstract base class defining the interface for domain classes.

    This interface enforces that all implementing classes must provide methods for 
    converting the object to a dictionary (`to_dict`) and to a data model 
    representation (`to_model`).

    Methods:
        to_dict(self): Converts the object to a dictionary representation.
        to_model(self): Converts the object to a data model instance.
    """
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def to_model(self):
        pass
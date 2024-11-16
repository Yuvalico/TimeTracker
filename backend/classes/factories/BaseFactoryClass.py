from abc import ABC, abstractmethod

class BaseFactory(ABC):
    """
    An abstract base class for factory classes.

    This class defines a common interface for factory classes, enforcing the implementation
    of a `create` method for creating objects of different types.

    Methods:
        create(type: str, **kwargs) -> object | None: 
            Creates an object of the specified type. (Static Method)
    """
    @staticmethod
    @abstractmethod
    def create(type: str, **kwargs) -> object | None:
        """
        Creates an object of the specified type.

        Args:
            type (str): The type of object to create.
            **kwargs: Keyword arguments to be passed to the constructor of the object.

        Returns:
            object | None: An instance of the specified type if successful, otherwise None.
        """
        pass
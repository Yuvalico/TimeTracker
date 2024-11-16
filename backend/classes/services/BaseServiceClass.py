from abc import ABC
from classes.domainclasses.DomainClassInterface import DomainClassInterface
from classes.repositories.BaseRepository import BaseRepository
from classes.validators.BaseValidator import ValidatorInterface
from classes.factories.DomainClassFactory import DomainClassFactory

class BaseService(ABC):
    """
    A base class for all service classes, providing common functionality 
    and promoting consistency.

    This class defines common methods for saving, updating, and deleting domain objects,
    including validation using a `ValidatorInterface` and object creation using a `DomainClassFactory`.

    Methods:
        _save(self, repository: BaseRepository, obj: DomainClassInterface): 
            Saves a domain object to the repository after validation.
        _update(self, repository: BaseRepository, obj: DomainClassInterface): 
            Updates a domain object in the repository after validation.
        _delete(self, repository: BaseRepository, obj: DomainClassInterface): 
            Deletes a domain object from the repository after validation.
    """

    def __init__(self, validator: ValidatorInterface, factory: DomainClassFactory):
        """
        Initializes the BaseService with a validator and a factory.

        Args:
            validator (ValidatorInterface): An instance of a validator class for validating domain objects.
            factory (DomainClassFactory): An instance of a factory class for creating domain objects.
        """
        self.validator = validator
        self.factory = factory
    
    def _save(self, repository: BaseRepository, obj: DomainClassInterface):
        """
        Saves a domain object to the repository after validation.

        Args:
            repository (BaseRepository): The repository to save the object to.
            obj (DomainClassInterface): The domain object to save.

        Returns:
            RC: A result code indicating success or failure of the operation.
        """
        validation_result = self.validator.validate(obj)  
        if not validation_result.is_ok():
            return validation_result
        
        return repository.save(obj)
        
    def _update(self, repository: BaseRepository, obj: DomainClassInterface):
        """
        Updates a domain object in the repository after validation.

        Args:
            repository (BaseRepository): The repository to update the object in.
            obj (DomainClassInterface): The domain object to update.

        Returns:
            RC: A result code indicating success or failure of the operation.
        """
        validation_result = self.validator.validate(obj)  
        if not validation_result.is_ok():
            return validation_result
        
        return repository.update(obj)
        
    def _delete(self, repository: BaseRepository, obj: DomainClassInterface):
        """
        Deletes a domain object from the repository after validation.

        Args:
            repository (BaseRepository): The repository to delete the object from.
            obj (DomainClassInterface): The domain object to delete.

        Returns:
            RC: A result code indicating success or failure of the operation.
        """
        validation_result = self.validator.validate(obj)  
        if not validation_result.is_ok():
            return validation_result
        
        return repository.delete(obj)

        


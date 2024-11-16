from classes.domainclasses.User import User
from classes.domainclasses.Company import Company
from classes.domainclasses.TimeStamp import TimeStamp
from classes.factories.BaseFactoryClass import BaseFactory
from classes.utilities.RC import RC, E_RC
from cmn_utils import *

class DomainClassFactory(BaseFactory):
    """
    A factory class for creating domain class instances.

    This factory provides a centralized way to create instances of different domain classes 
    (User, Company, TimeStamp) based on a given model type.

    Methods:
        create(self, model_type: str, **kwargs) -> User | Company | TimeStamp | RC: 
            Creates an instance of the specified domain class type.
    """
    def create(self, model_type: str, **kwargs) -> User | Company | TimeStamp | RC:
        """
        Creates an instance of the specified domain class type.

        Args:
            model_type (str): The type of domain class to create ('user', 'company', or 'timestamp').
            **kwargs: Keyword arguments to be passed to the constructor of the domain class.

        Returns:
            User | Company | TimeStamp | RC: 
                An instance of the specified domain class if successful, 
                otherwise an RC object indicating an error.
        """
        try:
            if model_type == 'user':
                return User(**kwargs)
            elif model_type == 'company':
                return Company(**kwargs)
            elif model_type == 'timestamp':
                return TimeStamp(**kwargs)
            else:
                return RC(E_RC.RC_INVALID_INPUT, f"{model_type} is an invalid domain class type")
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_INVALID_INPUT, f"Server Error When Creating Domain Class")
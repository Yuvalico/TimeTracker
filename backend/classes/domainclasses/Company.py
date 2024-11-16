from dataclasses import dataclass
from classes.domainclasses.DomainClassInterface import DomainClassInterface

@dataclass
class Company(DomainClassInterface):
    """
    Represents a company entity.

    Attributes:
        company_id (str): The unique identifier of the company.
        company_name (str): The name of the company.
        is_active (bool): Indicates whether the company is currently active.
        users (list): A list of users associated with the company (optional).

    Methods:
        to_dict(self): Converts the company object to a dictionary representation.
        to_model(self): Converts the company object to a CompanyModel instance.
    """
    company_id: str
    company_name: str
    is_active: bool
    users: list = None
    
    def to_dict(self):
        """
        Converts the company object to a dictionary.

        Returns:
            dict: A dictionary representation of the company object.
        """
        return {
            'company_id': str(self.company_id),  
            'company_name': self.company_name,
            'is_active': self.is_active
        }
    def to_model(self):
        """
        Converts the company object to a CompanyModel instance.

        Returns:
            CompanyModel: A CompanyModel instance representing the company.
        """
        from models import CompanyModel
        return CompanyModel(
            company_id = self.company_id if self.company_id else None,  
            company_name = self.company_name,
            is_active = self.is_active
        )
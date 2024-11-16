
from cmn_utils import iso2datetime, datetime2iso
from dataclasses import dataclass
from datetime import datetime, timezone
from cmn_utils import print_exception, datetime2iso, iso2datetime
from classes.domainclasses.Company import Company
from classes.domainclasses.DomainClassInterface import DomainClassInterface


@dataclass
class User(DomainClassInterface):
    """
    Represents a user entity.

    Attributes:
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        mobile_phone (str): The mobile phone number of the user.
        company_id (str): The unique identifier of the company the user belongs to.
        role (str): The role of the user within the company.
        permission (int): The permission level assigned to the user.
        pass_hash (str): The hashed password of the user.
        is_active (bool): Indicates whether the user account is active.
        salary (float): The salary of the user.
        work_capacity (float): The work capacity of the user (e.g., full-time, part-time).
        employment_start (datetime): The start date of the user's employment.
        employment_end (datetime): The end date of the user's employment.
        weekend_choice (str): The preferred weekend days for the user.
        company (Company, optional): The Company object associated with the user.

    Methods:
        to_dict(self): Converts the User object to a dictionary representation.
        to_model(self): Converts the User object to a UserModel instance.
    """
    email: str
    first_name: str
    last_name: str
    mobile_phone: str
    company_id: str
    role: str
    permission: int
    pass_hash: str
    is_active: bool
    salary: float  # You might want to use the Salary value object here
    work_capacity: float
    employment_start: datetime
    employment_end: datetime
    weekend_choice: str
    company: Company = None
    
    
    def to_dict(self):
        """
        Converts the User object to a dictionary.

        Returns:
            dict: A dictionary representation of the User object (excluding the 'pass_hash' for security).
        """
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'mobile_phone': self.mobile_phone,
            'company_id': str(self.company_id),  # Convert UUID to string
            'role': self.role,
            'permission': self.permission,
            # Exclude 'pass_hash' for security reasons
            'is_active': self.is_active,
            'salary': str(self.salary) if self.salary else None,  # Handle potential None values
            'work_capacity': str(self.work_capacity) if self.work_capacity else None,
            'employment_start': datetime2iso(self.employment_start),
            'employment_end': datetime2iso(self.employment_end),
            'weekend_choice': self.weekend_choice
        }
        
    def to_model(self):
        """
        Converts the User object to a UserModel instance.

        Returns:
            UserModel: A UserModel instance representing the user.
        """
        from models import UserModel
        return UserModel(
            email= self.email,
            first_name= self.first_name,
            last_name= self.last_name,
            mobile_phone= self.mobile_phone,
            company_id= self.company_id,
            role= self.role,
            permission= self.permission,
            pass_hash = self.pass_hash,
            is_active= self.is_active,
            salary= float(self.salary) if self.salary else 0,  
            work_capacity= float(self.work_capacity) if self.work_capacity else 0,
            employment_start = self.employment_start,
            employment_end = self.employment_end,
            weekend_choice = self.weekend_choice
        )
        
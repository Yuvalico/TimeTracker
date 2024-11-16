from classes.domainclasses.DomainClassInterface import DomainClassInterface
from classes.validators.BaseValidator import ValidatorInterface
from classes.domainclasses.User import User
from classes.domainclasses.Company import Company
from classes.domainclasses.TimeStamp import TimeStamp
from classes.utilities.Permission import E_PERMISSIONS
from classes.utilities.RC import RC, E_RC
from datetime import datetime
import re

class ModelValidator(ValidatorInterface):
    """
    Validator class for domain models.

    This class implements the ValidatorInterface and provides validation logic for
    User, Company, and TimeStamp objects. It checks for data type correctness, 
    value ranges, and other constraints to ensure data integrity.

    Methods:
        validate(self, obj: DomainClassInterface) -> RC: Validates a given domain object.
        _validate_user(self, user: User) -> RC: Validates a User object.
        _validate_company(self, company: Company) -> RC: Validates a Company object.
        _validate_timestamp(self, timestamp: TimeStamp) -> RC: Validates a TimeStamp object.
    """
    def validate(self, obj: DomainClassInterface) -> RC:
        """
        Validates a given domain object.

        Dispatches the validation to specific methods based on the object type.

        Args:
            obj (DomainClassInterface): The domain object to validate.

        Returns:
            RC: An RC object indicating the validation result.
        """
        if isinstance(obj, User):
            return self._validate_user(obj)
        elif isinstance(obj, Company):
            return self._validate_company(obj)
        elif isinstance(obj, TimeStamp):
            return self._validate_timestamp(obj)
        else:
            return RC(E_RC.RC_INVALID_INPUT, "Unsupported object type for validation")

    def _validate_user(self, user: User) -> RC:
        """
        Validates a User object.

        Checks for various constraints on user attributes like email format, name validity,
        permission levels, salary, work capacity, employment dates, and weekend choice.

        Args:
            user (User): The User object to validate.

        Returns:
            RC: An RC object indicating the validation result.
        """
        if not user.email:
            return RC(E_RC.RC_INVALID_INPUT, "Email is required.")
        if not isinstance(user.email, str) or not re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid email format.")

        if not user.first_name:
            return RC(E_RC.RC_INVALID_INPUT, "First name required.")
        if not user.last_name:
            return RC(E_RC.RC_INVALID_INPUT, "Last name required.")
        if not isinstance(user.first_name, str) or not user.first_name.strip():
            return RC(E_RC.RC_INVALID_INPUT, "First name must be a non-empty string.")
        if not isinstance(user.last_name, str) or not user.last_name.strip():
            return RC(E_RC.RC_INVALID_INPUT, "Last name must be a non-empty string.")
        if len(user.first_name) > 255:  
            return RC(E_RC.RC_INVALID_INPUT, "First Name cannot exceed 255 characters.")
        if len(user.last_name) > 255:  
            return RC(E_RC.RC_INVALID_INPUT, "Last Name cannot exceed 255 characters.")

        if user.mobile_phone:
            if not isinstance(user.mobile_phone, str) or not re.match(r"^\d{10}$", user.mobile_phone):  
                return RC(E_RC.RC_INVALID_INPUT, "Invalid mobile phone format.")

        if user.company_id and not isinstance(user.company_id, str): 
            return RC(E_RC.RC_INVALID_INPUT, "Invalid company ID format.")

        if not user.role:
            return RC(E_RC.RC_INVALID_INPUT, "Role is required.")
        if not isinstance(user.role, str) or not user.role.strip():
            return RC(E_RC.RC_INVALID_INPUT, "Role must be a non-empty string.")
        if len(user.role) > 255:  
            return RC(E_RC.RC_INVALID_INPUT, "Role cannot exceed 255 characters.")

        try:
            E_PERMISSIONS(user.permission)  
        except ValueError:
            return RC(E_RC.RC_INVALID_INPUT, "Invalid permission value.")

        if not isinstance(user.is_active, bool):
            return RC(E_RC.RC_INVALID_INPUT, "is_active must be a boolean value (True/False).")

        if not isinstance(user.salary, (int, float)) or user.salary < 0:
            return RC(E_RC.RC_INVALID_INPUT, "Invalid salary value. Must be a positive number")

        if not isinstance(user.work_capacity, (int, float)) or user.work_capacity < 0 or user.work_capacity > 24:
            return RC(E_RC.RC_INVALID_INPUT, "Invalid work capacity value. Value must be a number between 0 and 24")

        if not isinstance(user.employment_start, datetime):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid employment start date.")
        if user.employment_end and not isinstance(user.employment_end, datetime):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid employment end date.")
        if user.employment_end and user.employment_end < user.employment_start:
            return RC(E_RC.RC_INVALID_INPUT, "Employment end date cannot be before the start date.")

        if user.weekend_choice and not isinstance(user.weekend_choice, str):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid weekend choice format.")

        return RC(E_RC.RC_OK, "User Validation Succesfull")

    def _validate_company(self, company: Company) -> RC:
        """
        Validates a Company object.

        Checks for company name validity and active status.

        Args:
            company (Company): The Company object to validate.

        Returns:
            RC: An RC object indicating the validation result.
        """
        if not company.company_name:
            return RC(E_RC.RC_INVALID_INPUT, "Company name is required.")
        
        if not isinstance(company.company_name, str) or not company.company_name.strip():
            return RC(E_RC.RC_INVALID_INPUT, "Company name must be a non-empty string.")
        
        if len(company.company_name) > 255:  
            return RC(E_RC.RC_INVALID_INPUT, "Company name cannot exceed 255 characters.")
        
        if not isinstance(company.is_active, bool):
            return RC(E_RC.RC_INVALID_INPUT, "is_active must be a boolean value (True/False).")

        return RC(E_RC.RC_OK, "Company Validation Succesfull")
    
    def _validate_timestamp(self, timestamp: TimeStamp) -> RC:
        """
        Validates a TimeStamp object.

        Checks for various constraints on timestamp attributes, including user email format,
        punch type, timestamps, details, and reporting type.

        Args:
            timestamp (TimeStamp): The TimeStamp object to validate.

        Returns:
            RC: An RC object indicating the validation result.
        """
        if not timestamp.user_email:
            return RC(E_RC.RC_INVALID_INPUT, "User email is required.")
        if not isinstance(timestamp.user_email, str) or not re.match(r"[^@]+@[^@]+\.[^@]+", timestamp.user_email):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid user email format.")

        if not timestamp.entered_by:
            return RC(E_RC.RC_INVALID_INPUT, "Entered by is required.")
        if not isinstance(timestamp.entered_by, str) or not re.match(r"[^@]+@[^@]+\.[^@]+", timestamp.entered_by):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid entered by email format.")

        if not isinstance(timestamp.punch_type, int) or timestamp.punch_type < 0 or timestamp.punch_type > 3:
            return RC(E_RC.RC_INVALID_INPUT, "Invalid punch type.")

        if not timestamp.punch_in_timestamp:
            return RC(E_RC.RC_INVALID_INPUT, "Punch in timestamp is required.")
        if not isinstance(timestamp.punch_in_timestamp, datetime):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid punch in timestamp format.")

        if timestamp.punch_out_timestamp and not isinstance(timestamp.punch_out_timestamp, datetime):
            return RC(E_RC.RC_INVALID_INPUT, "Invalid punch out timestamp format.")

        if timestamp.punch_out_timestamp and timestamp.punch_out_timestamp < timestamp.punch_in_timestamp:
            return RC(E_RC.RC_INVALID_INPUT, "Punch out timestamp cannot be before punch in timestamp.")

        if timestamp.detail:
            if not isinstance(timestamp.detail, str) or not timestamp.detail.strip():
                return RC(E_RC.RC_INVALID_INPUT, "Detail must be a non-empty string.")
            if timestamp.detail and len(timestamp.detail) > 255:  
                return RC(E_RC.RC_INVALID_INPUT, "Timestamp Details cannot exceed 255 characters.")

        if not timestamp.reporting_type:
            return RC(E_RC.RC_INVALID_INPUT, "Reporting type is required.")
        if not isinstance(timestamp.reporting_type, str) or not timestamp.reporting_type.strip() and timestamp.reporting_type not in ["work, paidoff, unpaidoff"]:
            return RC(E_RC.RC_INVALID_INPUT, "Reporting type must be a non-empty string. Valid Values are [work, paidoff, unpaidoff]")

        return RC(E_RC.RC_OK, "Timestamp Validation Succesfull")
from classes.domainclasses.User import User
from cmn_utils import *
import bcrypt
from classes.validators.ModelValidator import ModelValidator
from classes.repositories.UserRepository import UserRepository
from classes.repositories.CompanyRepository import CompanyRepository
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.domainclasses.Company import Company
from classes.utilities.Permission import Permission
from classes.utilities.RC import RC, E_RC
from classes.services.BaseServiceClass import BaseService


class UserService(BaseService):
    """
    A service class for managing user accounts and their associated data.

    This class provides methods for creating, updating, deleting, and retrieving user information,
    including password management and user activation status. It enforces authorization checks
    based on user permissions to ensure secure access and modification of user data.

    Methods:
        create_user(self, email: str, first_name: str, last_name: str, company_name: str,
                        role: str, permission: int, password: str, salary: float, work_capacity: float,
                        employment_start_str: str, user_permission: int,
                        mobile_phone: str = None, employment_end_str: str = None, weekend_choice: str = None) -> RC:
                        Creates a new user account with the provided details.

        update_user(self, user_email: str, user_permission: int, first_name: str = None, last_name: str = None,
                        company_id: str = None, role: str = None, permission: int = None,
                        mobile_phone: str = None, password: str = None, salary: float = None,
                        work_capacity: float = None, employment_start_str: str = None,
                        employment_end_str: str = None, weekend_choice: str = None) -> RC:
                        Updates an existing user account with the provided details.

        delete_user(self, user_permission, user_email: str, employment_end_str: str = None) -> RC:
                        Deactivates a user account (soft delete).

        change_password(self, user_permission: int, current_user_email: str, current_user_company: int, user_email: str, new_password: str) -> RC:
                        Changes the password of a user account.

        reactivate_user(self, user_permission: int, user_to_reactivate_email: str) -> RC:
                        Reactivates a deactivated user account.

        get_user_by_email(self, user_permission: int, current_user_email: str, user_company_id, requested_user_email: str) -> RC|dict:
                        Retrieves user information by email address.

        get_active_users(self, user_permission: int, user_company_id: str = None) -> list:
                        Retrieves a list of active user accounts.

        get_inactive_users(self, user_permission: int, user_company_id: str = None) -> list:
                        Retrieves a list of inactive user accounts.

        get_all_users(self, user_permission: int, user_company_id: str = None) -> list:
                        Retrieves a list of all user accounts (active and inactive).
    """
    def __init__(self, user_repository: UserRepository, company_repository: CompanyRepository, validator: ModelValidator, factory: DomainClassFactory):
        """Initializes UserService with required repositories and utilities."""
        super().__init__(validator, factory)
        self.user_repository = user_repository
        self.company_repository = company_repository

    def create_user(self, email: str, first_name: str, last_name: str, company_name: str,
                   role: str, permission: int, password: str, salary: float, work_capacity: float,
                   employment_start_str: str, user_permission: int,
                   mobile_phone: str = None, employment_end_str: str = None, weekend_choice: str = None) -> RC:
        """Creates a new user account.

        Performs necessary checks and validations before creating and saving the user object.

        Args:
            email (str): The email address of the new user.
            first_name (str): The first name of the new user.
            last_name (str): The last name of the new user.
            company_name (str): The name of the company the user belongs to.
            role (str): The role of the user in the company.
            permission (int): The permission level of the new user.
            password (str): The password for the new user account.
            salary (float): The salary of the new user.
            work_capacity (float): The work capacity of the new user.
            employment_start_str (str): ISO formatted string representing the employment start date.
            user_permission (int): The permission level of the user creating this account.
            mobile_phone (str, optional): The mobile phone number of the new user. Defaults to None.
            employment_end_str (str, optional): ISO formatted string representing the employment end date. Defaults to None.
            weekend_choice (str, optional): The preferred weekend days of the new user. Defaults to None.

        Returns:
            RC: An RC object indicating the success or failure of the operation.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        if not first_name or not last_name or not email or not password or not company_name\
            or not role or not permission or not salary or not work_capacity or not employment_start_str:
                return RC(E_RC.RC_INVALID_INPUT, "Missing mandatory user field")
            
        company: Company = self.company_repository.get_company_by_name(company_name)
        if isinstance(company, RC):
            return company  

        existing_user: User | RC = self.user_repository.get_user_by_email(email)
        if not isinstance(existing_user, RC):
            return RC(E_RC.RC_INVALID_INPUT, 'User email already exists')

        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'company_id': company.company_id, 
            'role': role,
            'permission': permission,
            'pass_hash': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'is_active': True,
            'salary': float(salary),
            'work_capacity': float(work_capacity),
            'employment_start': iso2datetime(employment_start_str),
            'employment_end': iso2datetime(employment_end_str),
            'weekend_choice': weekend_choice,
            'mobile_phone': mobile_phone
            }
        new_user: User = self.factory.create("user", **user_data)
        if isinstance(new_user, RC):
            return new_user

        return self._save(self.user_repository, new_user)

    def update_user(self, user_email: str, user_permission: int, first_name: str = None, last_name: str = None,
                    company_id: str = None, role: str = None, permission: int = None,
                    mobile_phone: str = None, password: str = None, salary: float = None,
                    work_capacity: float = None, employment_start_str: str = None,
                    employment_end_str: str = None, weekend_choice: str = None) -> RC:
        """Updates an existing user account.

        Allows updating various user attributes and performs necessary authorization checks.

        Args:
            user_email (str): The email of the user to update.
            user_permission (int): The permission level of the user making the update request.
            first_name (str, optional): The updated first name. Defaults to None.
            last_name (str, optional): The updated last name. Defaults to None.
            company_id (str, optional): The updated company ID. Defaults to None.
            role (str, optional): The updated role. Defaults to None.
            permission (int, optional): The updated permission level. Defaults to None.
            mobile_phone (str, optional): The updated mobile phone number. Defaults to None.
            password (str, optional): The updated password. Defaults to None.
            salary (float, optional): The updated salary. Defaults to None.
            work_capacity (float, optional): The updated work capacity. Defaults to None.
            employment_start_str (str, optional): ISO formatted string for the updated employment start date. Defaults to None.
            employment_end_str (str, optional): ISO formatted string for the updated employment end date. Defaults to None.
            weekend_choice (str, optional): The updated preferred weekend days. Defaults to None.

        Returns:
            RC: An RC object indicating the success or failure of the update operation.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if company_id:
            user.company_id = company_id
        if role:
            user.role = role
        if permission is not None:
            user.permission = permission
        if mobile_phone:
            user.mobile_phone = mobile_phone
        if password:
            user.pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if salary is not None:
            user.salary = float(salary)
        if work_capacity is not None:
            user.work_capacity = float(work_capacity)
        if employment_start_str:
            user.employment_start = iso2datetime(employment_start_str)
        if employment_end_str:
            user.employment_end = iso2datetime(employment_end_str)
        if weekend_choice:
            user.weekend_choice = weekend_choice

        return self._update(self.user_repository, user)


    def delete_user(self, user_permission, user_email: str, employment_end_str: str = None) -> RC:
        """Deactivates a user account (soft delete).

        Sets the user's 'is_active' status to False and optionally updates the employment end date.

        Args:
            user_permission (int): The permission level of the user requesting the deletion.
            user_email (str): The email of the user to deactivate.
            employment_end_str (str, optional): ISO formatted string for the employment end date. Defaults to None.

        Returns:
            RC: An RC object indicating success or failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user
        
        user.is_active = False
        user.employment_end = iso2datetime(employment_end_str)
        
        return self._update(self.user_repository, user)

    def change_password(self, user_permission: int, current_user_email: str, current_user_company: int, user_email: str, new_password: str) -> RC:
        """Changes the password of a user account.

        Performs authorization checks to ensure only authorized users can change passwords.

        Args:
            user_permission (int): The permission level of the user requesting the password change.
            current_user_email (str): The email of the user making the request.
            current_user_company (int): The company ID of the user making the request.
            user_email (str): The email of the user whose password needs to be changed.
            new_password (str): The new password.

        Returns:
            RC: An RC object indicating success or failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user
        
        if perm.is_net_admin() or \
            (perm.is_employer() and current_user_company == user.company_id) or \
                (perm.is_employee() and current_user_email == user.email):
                    
            user.pass_hash=bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return self._update(self.user_repository, user)
        
        return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
    
    def reactivate_user(self, user_permission: int, user_to_reactivate_email: str) -> RC:
        """Reactivates a deactivated user account.

        Sets the user's 'is_active' status to True and clears the employment end date.

        Args:
            user_permission (int): The permission level of the user requesting the reactivation.
            user_to_reactivate_email (str): The email of the user to reactivate.

        Returns:
            RC: An RC object indicating success or failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
            
        user: User | RC = self.user_repository.get_user_by_email(user_to_reactivate_email)
        if isinstance(user, RC):
            return user
        
        user.is_active = True
        user.employment_end = None
        
        return self._update(self.user_repository, user)

    def get_user_by_email(self, user_permission: int, current_user_email: str, user_company_id, requested_user_email: str) -> RC|dict:
        """Retrieves user information by email address.

        Performs authorization checks based on user permissions.

        Args:
            user_permission (int): The permission level of the user making the request.
            current_user_email (str): The email of the user making the request.
            user_company_id (int): The company ID of the user making the request.
            requested_user_email (str): The email of the user whose information is requested.

        Returns:
            RC|dict: A dictionary containing user information if successful, or an RC object indicating failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        requested_user: User = self.user_repository.get_user_by_email(requested_user_email)
        
        if perm.is_employer():
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            if user_company_id != requested_user.company_id:
                return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
            
        if perm.is_employee() and current_user_email and current_user_email != requested_user.email:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        return requested_user.to_dict()
    
    def get_active_users(self, user_permission: int, user_company_id: str = None) -> list:
        """Retrieves a list of active user accounts.

        Performs authorization checks and filters users based on company ID if necessary.

        Args:
            user_permission (int): The permission level of the user making the request.
            user_company_id (str, optional): The company ID to filter users by. Defaults to None.

        Returns:
            list: A list of dictionaries, each containing information about an active user.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_net_admin():
            active_users: list[User] = self.user_repository.get_active_users()
        elif perm.is_employer:
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            
            active_users: list[User] = self.user_repository.get_active_users(user_company_id)
        else:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        user_data = []
        for user in active_users:
            user_dict = user.to_dict()
            user_dict['company_name'] = self.company_repository.get_company_by_id(user.company_id).company_name
            user_data.append(user_dict)

        return user_data
    
    def get_inactive_users(self, user_permission: int, user_company_id: str = None) -> list:
        """Retrieves a list of inactive user accounts.

        Performs authorization checks and filters users based on company ID if necessary.

        Args:
            user_permission (int): The permission level of the user making the request.
            user_company_id (str, optional): The company ID to filter users by. Defaults to None.

        Returns:
            list: A list of dictionaries, each containing information about an inactive user.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_net_admin():
            active_users: list[User] = self.user_repository.get_inactive_users()
        elif perm.is_employer:
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            
            active_users: list[User] = self.user_repository.get_inactive_users(user_company_id)
        else:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        user_data = []
        for user in active_users:
            user_dict = user.to_dict()
            user_dict['company_name'] = self.company_repository.get_company_by_id(user.company_id).company_name
            user_data.append(user_dict)

        return user_data

    def get_all_users(self, user_permission: int, user_company_id: str = None) -> list:
        """Retrieves a list of all user accounts (active and inactive).

        Performs authorization checks and filters users based on company ID if necessary.

        Args:
            user_permission (int): The permission level of the user making the request.
            user_company_id (str, optional): The company ID to filter users by. Defaults to None.

        Returns:
            list: A list of dictionaries, each containing information about a user.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_net_admin:
            users: list[User] = self.user_repository.get_users()  
            
        elif perm.is_employer():
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            users: list[User] = self.user_repository.get_active_users(user_company_id)
        else:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        user_data = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['company_name'] = self.company_repository.get_company_by_id(user.company_id).company_name
            user_data.append(user_dict)

        return user_data
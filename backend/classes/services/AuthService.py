from flask_jwt_extended import create_access_token, create_refresh_token
from models import User
from classes.utilities.RC import RC, E_RC
from classes.repositories.UserRepository import UserRepository
from classes.validators.ModelValidator import ModelValidator
from classes.services.BaseServiceClass import BaseService
from classes.factories.DomainClassFactory import DomainClassFactory
from cmn_utils import *
import bcrypt


class AuthService(BaseService):
    """
    A service class for handling authentication and authorization.

    This class provides methods for user login, token refresh, 
    and managing user permissions.

    Methods:
        login(self, email: str, password: str) -> tuple[str, str] | RC: 
            Authenticates a user and generates access and refresh tokens.
        refresh(self, current_user: str) -> tuple[str, str] | RC: 
            Refreshes an access token for a logged-in user.
    """
    def __init__(self, user_repository: UserRepository, validator: ModelValidator, factory: DomainClassFactory):
        """
        Initializes the AuthService with necessary dependencies.

        Args:
            user_repository (UserRepository): An instance of the UserRepository for user data access.
            validator (ModelValidator): An instance of the ModelValidator for data validation.
            factory (DomainClassFactory): An instance of the DomainClassFactory for creating domain objects.
        """
        super().__init__(validator, factory)
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> tuple[str, str] | RC:
        """
        Authenticates a user and generates access and refresh tokens.

        Args:
            email (str): The email address of the user.
            password (str): The password entered by the user.

        Returns:
            tuple[str, str] | RC: A tuple containing the access token and refresh token if successful, 
                                 otherwise an RC object indicating an error.
        """
        try:
            user: User | RC = self.user_repository.get_user_by_email(email)
            if isinstance(user, RC):
                return user

            if not user.pass_hash:
                return RC(E_RC.RC_INVALID_INPUT, 'Password not set for this user')

            if not bcrypt.checkpw(password.encode('utf-8'), user.pass_hash.encode('utf-8')):
                return RC(E_RC.RC_INVALID_INPUT, 'Invalid credentials')

            additional_claims = {
                'permission': user.permission,
                'company_id': user.company_id
            }
            access_token = create_access_token(
                identity=user.email,
                fresh=True,
                additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=user.email)

            return {"access_token" :access_token, 
                    "refresh_token": refresh_token,
                    "permission": user.permission,
                    "company_id": user.company_id
                    }

        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, 'Server error')

    def refresh(self, current_user: str) -> tuple[str, str] | RC:
        """
        Refreshes an access token for a logged-in user.

        Args:
            current_user (str): The email of the currently logged-in user.

        Returns:
            tuple[str, str] | RC: A tuple containing the new access token and new refresh token if successful, 
                                 otherwise an RC object indicating an error.
        """
        try:
            user: User | RC = self.user_repository.get_user_by_email(email=current_user)
            if isinstance(user, RC):
                return user

            additional_claims = {
                'permission': user.permission,
                'company_id': user.company_id
            }
            new_access_token = create_access_token(
                identity=current_user,
                fresh=False,
                additional_claims=additional_claims)
            
            new_refresh_token = create_refresh_token(identity=current_user)

            return {"new_access_token": new_access_token,
                    "new_refresh_token": new_refresh_token
                    }   

        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, 'Server error')
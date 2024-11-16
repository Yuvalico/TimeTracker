from models import *
from classes.domainclasses.User import User
from typing import List
from classes.utilities.RC import RC, E_RC
from classes.repositories.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    """
    A repository class for managing users in the database.

    This class provides methods for accessing and manipulating user data 
    in the database using SQLAlchemy.

    Methods:
        get_active_users(self, company_id: str = None) -> List[User]: Retrieves all active users, optionally filtered by company ID.
        get_inactive_users(self, company_id: str = None) -> List[User]: Retrieves all inactive users, optionally filtered by company ID.
        get_users(self, company_id: str = None) -> List[User]: Retrieves all users, optionally filtered by company ID.
        get_user_by_email(self, email: str) -> User | RC: Retrieves a user by their email address.
    """
    def __init__(self, db: SQLAlchemy):
        """
        Initializes the UserRepository with a SQLAlchemy database instance.

        Args:
            db (SQLAlchemy): The SQLAlchemy database instance.
        """
        super().__init__(db)

    def get_active_users(self, company_id: str = None) -> List[User]:
        """
        Retrieves all active users, optionally filtered by company ID.

        Args:
            company_id (str, optional): The ID of the company to filter by. Defaults to None.

        Returns:
            List[User]: A list of active users.
        """
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .filter(UserModel.is_active == True)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .filter(
                    UserModel.is_active == True,  
                    UserModel.company_id == company_id  
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]
    
    def get_inactive_users(self, company_id: str = None) -> List[User]:
        """
        Retrieves all inactive users, optionally filtered by company ID.

        Args:
            company_id (str, optional): The ID of the company to filter by. Defaults to None.

        Returns:
            List[User]: A list of inactive users.
        """
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .filter(UserModel.is_active == False)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(UserModel, CompanyModel)
                .filter(
                    UserModel.is_active == False,  
                    CompanyModel.company_id == company_id  
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]
    
    def get_users(self, company_id: str = None) -> List[User]:
        """
        Retrieves all users, optionally filtered by company ID.

        Args:
            company_id (str, optional): The ID of the company to filter by. Defaults to None.

        Returns:
            List[User]: A list of all users.
        """
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(UserModel, CompanyModel)
                .filter(
                    CompanyModel.company_id == company_id  
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]

    def get_user_by_email(self, email: str) -> User | RC:
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user.

        Returns:
            User | RC: The User object if found, otherwise an RC object indicating an error.
        """
        user: UserModel = UserModel.query.get(email)
        if user:
            return user.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"User not found for: {email}")
    
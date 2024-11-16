from models import CompanyModel, UserModel
from classes.domainclasses.User import User
from classes.domainclasses.Company import Company
from classes.utilities.RC import RC, E_RC
from cmn_utils import *
from typing import List
import bcrypt
from cmn_utils import print_exception, datetime2iso, iso2datetime
from flask_sqlalchemy import SQLAlchemy
from classes.repositories.BaseRepository import BaseRepository
from classes.utilities.Permission import E_PERMISSIONS



class CompanyRepository(BaseRepository):
    """
    A repository class for managing companies in the database.

    This class provides methods for accessing and manipulating company data 
    in the database using SQLAlchemy.

    Methods:
        get_all_companies(self) -> List[Company]: Retrieves all companies.
        get_all_active_companies(self) -> List[Company]: Retrieves all active companies.
        get_all_inactive_companies(self) -> List[Company]: Retrieves all inactive companies.
        get_company_admins(self, company_id: str) -> List[User]: Retrieves the admin users for a given company.
        get_company_by_id(self, company_id: str) -> Company | RC: Retrieves a company by its ID.
        get_company_by_name(self, company_name: str) -> Company: Retrieves a company by its name.
        get_company_users(self, company_id: str) -> List[User]: Retrieves all users belonging to a company.
    """
    def __init__(self, db: SQLAlchemy):
        """
        Initializes the CompanyRepository with a SQLAlchemy database instance.

        Args:
            db (SQLAlchemy): The SQLAlchemy database instance.
        """
        super().__init__(db)

    def get_all_companies(self) -> List[Company]:
        """
        Retrieves all companies from the database.

        Returns:
            List[Company]: A list of all companies.
        """
        companies = CompanyModel.query.all()
        return [company.to_class() for company in companies]
    
    def get_all_active_companies(self) -> List[Company]:
        """
        Retrieves all active companies from the database.

        Returns:
            List[Company]: A list of all active companies.
        """
        companies = CompanyModel.query.filter(CompanyModel.is_active == True).all()
        return [company.to_class() for company in companies]
    
    def get_all_inactive_companies(self) -> List[Company]:
        """
        Retrieves all inactive companies from the database.

        Returns:
            List[Company]: A list of all inactive companies.
        """
        companies = CompanyModel.query.filter(CompanyModel.is_active == False).all()
        return [company.to_class() for company in companies]
    
    def get_company_admins(self, company_id: str) -> List[User]:
        """
        Retrieves the admin users for a given company.

        Args:
            company_id (str): The ID of the company.

        Returns:
            List[User]: A list of admin users for the company.
        """
        if not company_id:
            return []
        
        admins = UserModel.query.filter(UserModel.company_id == company_id, UserModel.permission.in_([E_PERMISSIONS.employer, E_PERMISSIONS.net_admin]), 
                        UserModel.is_active == True ).all()
        
        return [admin.to_class() for admin in admins]

    def get_company_by_id(self, company_id: str) -> Company | RC:
        """
        Retrieves a company by its ID.

        Args:
            company_id (str): The ID of the company.

        Returns:
            Company | RC: The Company object if found, otherwise an RC object indicating an error.
        """
        company = CompanyModel.query.get(company_id)
        if company:
            return company.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"Company {company_id} not found")
    
    def get_company_by_name(self, company_name: str) -> Company:
        """
        Retrieves a company by its name.

        Args:
            company_name (str): The name of the company.

        Returns:
            Company: The Company object if found, otherwise None.
        """
        company: CompanyModel = CompanyModel.query.filter_by(company_name=company_name).first()
        if company:
            return company.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"Company {company_name} not found")
    
    def get_company_users(self, company_id: str) -> List[User]:
        """
        Retrieves all users belonging to a company.

        Args:
            company_id (str): The ID of the company.

        Returns:
            List[User]: A list of users belonging to the company.
        """
        users: UserModel = UserModel.query.filter_by(company_id=company_id, is_active=True).all()
        if users:
            return [user.to_class() for user in users]
        return []
    
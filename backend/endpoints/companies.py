from flask import Blueprint, request, jsonify
from models import db  
from classes.repositories import CompanyRepository
from classes.services.CompanyService import CompanyService
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.utilities.RC import RC, E_RC
from cmn_utils import *
from flask_jwt_extended import jwt_required

companies_blueprint = Blueprint('companies', __name__)
company_service: CompanyService = CompanyService(CompanyRepository.CompanyRepository(db), ModelValidator(), DomainClassFactory())

@companies_blueprint.route('/create-company', methods=['POST'])
@jwt_required() 
def create_company():
    """
    Creates a new company.

    Expects a JSON payload with `company_name`.
    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        data = request.get_json()
        company_name = data.get('company_name')

        rc: RC = company_service.create_company(company_name, user_permission)
        return rc.to_json()
        
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/update-company', methods=['PUT'])
@jwt_required() 
def update_company():
    """
    Updates an existing company.

    Expects a JSON payload with `company_id` and `company_name`.
    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
         
        data = request.get_json()
        company_id = data.get('company_id')  
        company_name = data.get('company_name')

        rc: RC = company_service.update_company(company_id, company_name, user_permission)
        return rc.to_json()
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/remove-company/<string:company_id>', methods=['PUT'])
@jwt_required() 
def remove_company(company_id):
    """
    Removes a company (soft delete).

    Requires a JWT token for authentication.

    Args:
        company_id (str): The ID of the company to remove.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
       
        rc: RC = company_service.delete_company(company_id, user_permission)
        return rc.to_json()
    
    except Exception as e:
        print_exception(e) 
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_companies():
    """
    Retrieves active companies.

    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response with company data, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        company_data = company_service.get_active_companies(user_permission)
        if isinstance(company_data, RC):
            return company_data.to_json()
        
        return jsonify(company_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/', methods=['GET'])
@jwt_required() 
def get_all_companies():
    """
    Retrieves all companies (active and inactive).

    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response with company data, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        company_data: dict|RC = company_service.get_all_companies(user_permission)
        if isinstance(company_data, RC):
            return company_data.to_json()
        
        return jsonify(company_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('<string:company_id>/users', methods=['GET'])
@jwt_required() 
def get_company_users(company_id):
    """
    Retrieves users associated with a specific company.

    Requires a JWT token for authentication.

    Args:
        company_id (str): The ID of the company.

    Returns:
        tuple: A JSON response with user data, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        users: dict|RC= company_service.get_company_users(company_id, user_permission, user_company_id)
        if isinstance(users, RC):
            return users.to_json()
        
        return jsonify(users), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/<string:company_id>', methods=['GET'])
@jwt_required() 
def get_company_details(company_id):
    """
    Retrieves details of a specific company.

    Requires a JWT token for authentication.

    Args:
        company_id (str): The ID of the company.

    Returns:
        tuple: A JSON response with company details, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        company: dict|RC = company_service.get_company_details(company_id, user_company_id, user_permission)
        if isinstance(company, RC):
            return company.to_json()
        
        return jsonify(company), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE
    
@companies_blueprint.route('/<string:company_id>/admins', methods=['GET'])
@jwt_required()
def get_company_admins(company_id):
    """
    Retrieves administrators associated with a specific company.

    Requires a JWT token for authentication.

    Args:
        company_id (str): The ID of the company.

    Returns:
        tuple: A JSON response with administrator data, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        admin_data: dict|RC = company_service.get_company_admins(company_id, user_company_id, user_permission)
        if isinstance(admin_data, RC):
            return admin_data.to_json()
        
        return jsonify(admin_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE
    
    
@companies_blueprint.route('/<string:company_id>/name', methods=['GET'])
@jwt_required()
def get_company_name_by_id(company_id):
    """
    Retrieves the name of a company by its ID.

    Requires a JWT token for authentication.

    Args:
        company_id (str): The ID of the company.

    Returns:
        tuple: A JSON response with the company name, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        name: dict|RC = company_service.get_company_name_by_id(company_id, user_company_id, user_permission)
        if isinstance(name, RC):
            return name.to_json()
        
        return jsonify(name), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE
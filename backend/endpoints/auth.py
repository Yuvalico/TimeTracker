from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from classes.utilities.RC import RC
from classes.repositories.UserRepository import UserRepository
from classes.services.AuthService import AuthService
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.utilities.RC import E_RC
from cmn_utils import *


auth_blueprint = Blueprint('auth', __name__)
auth_service: AuthService = AuthService(UserRepository(db), ModelValidator(), DomainClassFactory())  

@auth_blueprint.route('/login', methods=['POST'])
def login():
    """
    Handles user login requests.

    Expects a JSON payload with 'email' and 'password' fields.
    Generates access and refresh tokens upon successful authentication.

    Returns:
        tuple: A JSON response with tokens and user information, along with an HTTP status code.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        response: dict = auth_service.login(email, password)
        if isinstance(response, RC):
           return response.to_json()
    
        return jsonify({
            'access_token': response["access_token"], 
            'refresh_token': response["refresh_token"],
            'permission': response["permission"],
            'company_id': response["company_id"]
        }), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Handles token refresh requests.

    Requires a valid refresh token.
    Generates new access and refresh tokens.

    Returns:
        tuple: A JSON response with new tokens, along with an HTTP status code.
    """
    try:
        current_user = get_jwt_identity()
        
        response = auth_service.refresh(current_user)
        if isinstance(response, RC):
            return response.to_json()
        
        return jsonify({
            'access_token': response["new_access_token"], 
            'refresh_token': response["new_refresh_token"]
            }), E_RC.RC_OK
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE
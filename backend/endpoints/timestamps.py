from flask import Blueprint, request, jsonify
from models import db
from classes.repositories.UserRepository import UserRepository
from classes.repositories.TimeStampRepository import TimeStampRepository
from classes.services.TimeStampService import TimeStampService
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.utilities.RC import RC, E_RC 
from cmn_utils import print_exception, extract_jwt
from flask_jwt_extended import jwt_required

timestamps_bp = Blueprint('timestamps', __name__)

timestamp_service: TimeStampService = TimeStampService(TimeStampRepository(db), UserRepository(db), ModelValidator(), DomainClassFactory())

@timestamps_bp.route('/', methods=['POST'])
@jwt_required() 
def create_timestamp():
    """
    Creates a new timestamp record.

    Expects a JSON payload with details of the timestamp.
    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')
        entered_by_user = current_user_email
        punch_type = data.get('punch_type')
        reporting_type = data.get('reporting_type')
        detail = data.get('detail')
        punch_in = data.get("punch_in_timestamp")
        punch_out = data.get("punch_out_timestamp")
        
        rc: RC = timestamp_service.create_timestamp(user_email, entered_by_user, punch_type, punch_in, punch_out, reporting_type, detail, user_permission, user_company_id)
        return rc.to_json()

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/', methods=['GET'])
@jwt_required() 
def get_timestamps():
    """
    Retrieves all timestamp records.

    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response with timestamp data or an error message, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
         
        timestamps = timestamp_service.get_all_timestamps(user_permission)
        if isinstance(timestamps, RC):
            return timestamps.to_json()
            
        return jsonify(timestamps), E_RC.RC_OK

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/', methods=['PUT'])
@jwt_required() 
def punch_out():
    """
    Updates a timestamp record with punch-out information.

    Expects a JSON payload with punch-out details.
    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')
        entered_by = data.get('entered_by')
        reporting_type = data.get('reporting_type')
        detail = data.get('detail')

        rc : RC = timestamp_service.punch_out(user_email, entered_by, reporting_type, detail, user_permission, user_company_id)
        return rc.to_json()
    
    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE
    
@timestamps_bp.route('/<uuid:timestamp_uuid>', methods=['PUT'])
@jwt_required()
def edit(timestamp_uuid):
    """
    Edits an existing timestamp record.

    Expects a JSON payload with updated timestamp details.
    Requires a JWT token for authentication.

    Args:
        timestamp_uuid (UUID): The UUID of the timestamp to edit.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()

        punch_in_timestamp = data.get('punch_in_timestamp')
        punch_out_timestamp = data.get('punch_out_timestamp')
        punch_type = data.get('punch_type')
        detail = data.get('detail')
        reporting_type = data.get('reporting_type')
        
        rc: RC = timestamp_service.edit_timestamp(timestamp_uuid, punch_in_timestamp, punch_out_timestamp, punch_type, detail, reporting_type, current_user_email, user_permission, user_company_id)
        
        return rc.to_json()
    
    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/punch_in_status', methods=['POST'])
@jwt_required() 
def check_punch_in_status():
    """
    Checks if a user has an active punch-in timestamp.

    Expects a JSON payload with `user_email`.
    Requires a JWT token for authentication.

    Returns:
        tuple: A JSON response indicating whether the user has an active punch-in, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')

        answer: bool|RC= timestamp_service.check_punch_in_status(user_email, current_user_email, user_permission, user_company_id)
        if isinstance(answer, RC):
            return answer.to_json()
        
        elif answer:
            return jsonify({'has_punch_in': True}), E_RC.RC_OK
        else:
            return jsonify({'has_punch_in': False}), E_RC.RC_OK

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/<uuid:uuid>', methods=['DELETE'])
@jwt_required() 
def delete_timestamp(uuid):
    """
    Deletes a timestamp record.

    Requires a JWT token for authentication.

    Args:
        uuid (UUID): The UUID of the timestamp to delete.

    Returns:
        tuple: A JSON response indicating success or failure, with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        rc: RC = timestamp_service.delete_timestamp(uuid, current_user_email, user_permission, user_company_id)
        return rc.to_json()
        
    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE


@timestamps_bp.route('/getRange/<string:user_email>', methods=['GET'])
@jwt_required()
def get_timestamps_range(user_email):
    """
    Retrieves timestamp records within a specific date range for a user.

    Requires a JWT token for authentication.

    Args:
        user_email (str): The email of the user.
        start_date (str): The start date for the range (ISO format).
        end_date (str): The end date for the range (ISO format).

    Returns:
        tuple: A JSON response with timestamp data or an error message, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        timestamps = timestamp_service.get_timestamps_range(user_email, start_date_str, end_date_str, current_user_email, user_permission, user_company_id)
        if isinstance(timestamps, RC):
            return timestamps.to_json()
        
        return jsonify(timestamps), E_RC.RC_OK

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE
from flask import Blueprint, request, jsonify
from models import db
from cmn_utils import *
from flask_jwt_extended import jwt_required
from classes.repositories.CompanyRepository import CompanyRepository
from classes.utilities.RC import RC, E_RC
from classes.validators.ModelValidator import ModelValidator
from classes.repositories.UserRepository import UserRepository
from classes.repositories.TimeStampRepository import TimeStampRepository
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.services.ReportService import ReportService

reports_bp = Blueprint('reports', __name__)

report_service = ReportService(UserRepository(db), TimeStampRepository(db), CompanyRepository(db), ModelValidator(), DomainClassFactory())

@reports_bp.route('/generate-user', methods=['GET'])
@jwt_required()
def generate_user_report():
    """
    Generates a user report.

    Retrieves report parameters from the request arguments and generates a user-specific report.
    Requires a JWT token for authentication.

    Args:
        user_email (str): The email of the user for the report.
        date_range_type (str): The type of date range selection (e.g., 'this_week', 'last_month', 'custom').
        selected_year (int): The selected year for the report.
        selected_month (int): The selected month for the report.
        start_date_str (str): The start date for the report (ISO format).
        end_date_str (str): The end date for the report (ISO format).

    Returns:
        tuple: A JSON response with the report data or an error message, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        user_email = request.args.get('user_email')
        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        report = report_service.user_report(user_email, date_range_type, selected_year, selected_month, start_date_str, end_date_str, user_permission, user_company_id, current_user_email)
        if isinstance(report, RC):
            return report.to_json()
        
        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

@reports_bp.route('/generate-company', methods=['GET'])
@jwt_required()
def generate_company_summary_report():
    """
    Generates a company summary report.

    Retrieves report parameters from the request arguments and generates a summary report for a specific company.
    Requires a JWT token for authentication.

    Args:
        company_id (str): The ID of the company for the report.
        date_range_type (str): The type of date range selection (e.g., 'this_week', 'last_month', 'custom').
        selected_year (int): The selected year for the report.
        selected_month (int): The selected month for the report.
        start_date_str (str): The start date for the report (ISO format).
        end_date_str (str): The end date for the report (ISO format).

    Returns:
        tuple: A JSON response with the report data or an error message, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        company_id = request.args.get('company_id')
        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        report = report_service.company_summary(company_id, date_range_type, selected_year, selected_month, start_date_str, end_date_str, user_permission, user_company_id)
        if isinstance(report, RC):
            return report.to_json()
        
        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

@reports_bp.route('/generate-company-overview', methods=['GET'])
@jwt_required()
def generate_company_overview_report():
    """
    Generates a company overview report.

    Retrieves report parameters from the request arguments and generates an overview report across all companies.
    Requires a JWT token for authentication.

    Args:
        date_range_type (str): The type of date range selection (e.g., 'this_week', 'last_month', 'custom').
        selected_year (int): The selected year for the report.
        selected_month (int): The selected month for the report.
        start_date_str (str): The start date for the report (ISO format).
        end_date_str (str): The end date for the report (ISO format).

    Returns:
        tuple: A JSON response with the report data or an error message, along with an HTTP status code.
    """
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        report = report_service.company_overview(date_range_type, selected_year, selected_month, start_date_str, end_date_str, user_permission)
        if isinstance(report, RC):
            return report.to_json()

        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE


import traceback
from tabulate import tabulate
import datetime
import re
from datetime import datetime, timezone, timedelta
import psycopg2
from flask_jwt_extended import get_jwt_identity, get_jwt
from config import *

def print_exception(exception)-> None:
    """Prints a formatted exception message with relevant details.

    The exception message is formatted into a table with the following columns:
    - Timestamp
    - Exception Type
    - Exception Message
    - Filename
    - Line Number

    Args:
        exception: The exception object.
    """

    tb = traceback.extract_tb(exception.__traceback__)[-1]
    exception_type = type(exception).__name__
    exception_message = str(exception)
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    path_idx = find_timewatch_re(tb.filename)
    if -1 != path_idx:
        tb.filename = tb.filename[path_idx:]

    table_data = [
        [timestamp, "|", exception_type, "|", exception_message, "|", tb.filename, "|", tb.lineno]
    ]

    print(tabulate(table_data, tablefmt="simple", numalign="left", stralign="left"))

def find_timewatch_re(string)->int:
    """
    Finds the starting index of "timeWatch" or "tw" in a string.

    Args:
        string (str): The string to search in.

    Returns:
        int: The starting index of "timeWatch" or "tw" if found, -1 otherwise.
    """
    match = re.search(r"backend", string)
    if not match:
        match = re.search(r"timeWatch", string)
    if not match:
        match = re.search(r"tw", string)
    if not match:
        match = re.search(r"tt", string)

    return match.start() if match else -1

def get_db_connection(config: dict):
    """
    Establishes a connection to the PostgreSQL database.

    Args:
        config (dict): A dictionary containing database configuration parameters.

    Returns:
        psycopg2.connection: A database connection object.
    """
    conn = psycopg2.connect(
        host=config['DB_HOST'],
        database=config['DB_NAME'],
        user=config['DB_USER'],
        password=config['DB_PASSWORD']
    )
    return conn

def extract_jwt() -> tuple:
    """
    Extracts user information from the JWT token.

    Returns:
        tuple: A tuple containing the user's email, permission level, and company ID.
    """
    current_user_email = get_jwt_identity()
    claims = get_jwt()
    user_permission = claims.get('permission') 
    user_company_id = claims.get('company_id') 
    
    return current_user_email, user_permission, user_company_id


        
def calculate_work_capacity(user, start_date, end_date) -> float:
    """
    Calculates the total work capacity for a user within a given date range.

    Takes into account the user's weekend choice and daily work capacity.

    Args:
        user: The User object.
        start_date (datetime): The start date of the range.
        end_date (datetime): The end date of the range.

    Returns:
        float: The total work capacity in hours, rounded to 2 decimal places.
    """
    num_work_days = 0
    current_date = start_date
    while current_date <= end_date:
        if not user.weekend_choice or current_date.strftime('%A').lower() not in map(str.lower, user.weekend_choice.split(',')):
            num_work_days += 1
        current_date += timedelta(days=1)

    daily_work_capacity = float(user.work_capacity or 0)
    total_work_capacity = daily_work_capacity * num_work_days

    return round(total_work_capacity, 2)

def format_hours_to_hhmm(seconds) -> str:
    """
    Formats a duration in seconds to the HH:MM format.

    Args:
        seconds: The duration in seconds.

    Returns:
        A string representing the duration in HH:MM format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

def iso2datetime(iso_str: str) -> str:
    """
    Converts an ISO formatted string to a datetime object in UTC timezone.

    Args:
        iso_str (str): The ISO formatted string.

    Returns:
        datetime: The datetime object in UTC timezone.
    """
    date_time_obj : datetime=  datetime.fromisoformat(iso_str.replace('Z', '+00:00')) if iso_str else None
    if date_time_obj:
        return date_time_obj.replace(tzinfo=timezone.utc)
    else:
        return date_time_obj
    
def datetime2iso(date_time: datetime) -> str|None:
    """
    Converts a datetime object to an ISO formatted string.

    Args:
        date_time (datetime): The datetime object.

    Returns:
        str: The ISO formatted string.
    """
    return date_time.isoformat() if date_time else None

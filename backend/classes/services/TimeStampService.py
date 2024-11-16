from classes.domainclasses.User import User
from classes.domainclasses.TimeStamp import TimeStamp
from classes.utilities.RC import RC, E_RC
from cmn_utils import *
from datetime import datetime, timezone
from classes.validators.ModelValidator import ModelValidator
from classes.repositories.TimeStampRepository import TimeStampRepository
from classes.repositories.UserRepository import UserRepository
from classes.utilities.Permission import Permission
from classes.services.BaseServiceClass import BaseService
from classes.factories.DomainClassFactory import DomainClassFactory


class TimeStampService(BaseService):
    """
    A service class for managing timestamps, which represent user activity records.

    This class provides methods for creating, updating, deleting, and retrieving timestamps, 
    with proper authorization checks based on user permissions. It handles various scenarios 
    related to timestamps, such as punching in, punching out, editing existing timestamps, 
    and retrieving timestamps within a specific date range.

    Methods:
        create_timestamp(self, user_email: str, entered_by_user: str, punch_type: int, punch_in: str, punch_out: str,
                          reporting_type: str, detail: str, user_permission: int, user_company_id: str) -> RC: 
                          Creates a new timestamp record. Handles different cases for punch_in and punch_out values,
                          performs validation, and saves the timestamp to the repository.

        punch_out(self, user_email: str, entered_by: str, reporting_type: str, detail: str, user_permission: int,
                  user_company_id: str) -> RC: 
                  Updates an existing timestamp with punch-out information. Retrieves the latest punch-in timestamp
                  for the user and updates it with the current time and provided details.

        edit_timestamp(self, timestamp_uuid: str, punch_in_timestamp_str: str, punch_out_timestamp_str: str, punch_type: int,
                       detail: str, reporting_type: str, current_user_email: str, user_permission: int,
                       user_company_id: str) -> RC: 
                       Edits an existing timestamp record. Allows updating various fields of the timestamp and performs
                       authorization checks to ensure only authorized users can edit.

        delete_timestamp(self, uuid: str, current_user_email: str, user_permission: int, user_company_id: str) -> RC: 
                       Deletes a timestamp record. Retrieves the timestamp by its UUID and performs authorization checks
                       before deleting it from the repository.

        get_timestamps_range(self, user_email: str, start_date_str: str, end_date_str: str, current_user_email: str,
                             user_permission: int, user_company_id: str) -> list | RC: 
                             Retrieves timestamps within a specific date range. Performs authorization checks and
                             returns a list of timestamps within the given range for the specified user.

        check_punch_in_status(self, user_email: str, current_user_email ,user_permission: int, user_company_id: str) -> bool | RC: 
                             Checks if a user is currently punched in. Retrieves the latest timestamp for the user and
                             checks if it has a punch_out_timestamp.

        get_all_timestamps(self, user_permission: int) -> list | RC: 
                             Retrieves all timestamp records. Performs authorization checks and returns a list of all
                             timestamps in the repository.

        _iso_str_to_utc_datetime(self, date_str: str): 
                             Converts an ISO formatted date string to a datetime object in UTC timezone. Handles potential
                             ValueError exceptions during the conversion.
    """
    def __init__(self, timestamp_repository: TimeStampRepository, user_repository: UserRepository, validator: ModelValidator, factory: DomainClassFactory):
        """
        Initializes the TimeStampService with necessary dependencies.

        Args:
            timestamp_repository (TimeStampRepository): An instance of the TimeStampRepository for timestamp data access.
            user_repository (UserRepository): An instance of the UserRepository for user data access.
            validator (ModelValidator): An instance of the ModelValidator for data validation.
            factory (DomainClassFactory): An instance of the DomainClassFactory for creating domain objects.
        """
        super().__init__(validator, factory)
        self.timestamp_repository = timestamp_repository
        self.user_repository = user_repository

    def create_timestamp(self, user_email: str, entered_by_user: str,
                         punch_type: int, punch_in: str, punch_out: str,
                         reporting_type: str, detail: str,
                         user_permission: int,
                         user_company_id: str) -> RC:
        """Creates a new timestamp record.

        Handles different cases for punch_in and punch_out values, performs 
        validation, and saves the timestamp to the repository.

        Args:
            user_email (str): The email of the user for whom the timestamp is created.
            entered_by_user (str): The email of the user who created the timestamp.
            punch_type (int): The type of punch (e.g., work start, break start, etc.).
            punch_in (str): ISO formatted string representing the punch-in time. Can be None.
            punch_out (str): ISO formatted string representing the punch-out time. Can be None.
            reporting_type (str): The type of reporting for the timestamp (e.g., 'Work', 'Vacation').
            detail (str): Additional details about the timestamp.
            user_permission (int): The permission level of the user making the request.
            user_company_id (str): The company ID of the user.

        Returns:
            RC: An RC object indicating success or failure, with potential error messages.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee() and entered_by_user != user_email:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user

        if perm.is_employer() and user_company_id != user.company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        
        if punch_in:
            punch_in_datetime = self._iso_str_to_utc_datetime(punch_in)
            if isinstance(punch_in_datetime, RC):
                return punch_in_datetime
            
        if punch_out:
            punch_out_datetime= self._iso_str_to_utc_datetime(punch_out)
            if isinstance(punch_out_datetime, RC):
                return punch_out_datetime
            
        if not punch_in and not punch_out:
            punch_in_timestamp = datetime.now(timezone.utc)
            new_timestamp_data: dict = {
                'user_email': user_email,
                'entered_by': entered_by_user,
                'punch_type': punch_type,
                'punch_in_timestamp': punch_in_timestamp,
                'reporting_type': reporting_type,
                'detail': detail
                }
    
        elif punch_in and not punch_out:
            new_timestamp_data: dict = {
                'user_email': user_email,
                'entered_by': entered_by_user,
                'punch_type': punch_type,
                'punch_in_timestamp': punch_in_datetime,
                'reporting_type': reporting_type,
                'detail': detail
                }   

        elif punch_in and punch_out:
            if punch_in_datetime > punch_out_datetime:
                return RC(E_RC.RC_INVALID_INPUT, 'Start time should be earlier than end time')
            
            new_timestamp_data: dict = {
                'user_email': user_email,
                'entered_by': entered_by_user,
                'punch_type': punch_type,
                'punch_in_timestamp': punch_in_datetime,
                'punch_out_timestamp': punch_out_datetime,
                'reporting_type': reporting_type,
                'detail': detail
                }
        
        else:
            return RC(E_RC.RC_INVALID_INPUT, 'Start time should be earlier than end time')

        new_timestamp: TimeStamp = self.factory.create("timestamp", **new_timestamp_data)
        if isinstance(new_timestamp, RC):
            return new_timestamp
        
        return self._save(self.timestamp_repository, new_timestamp)

    def punch_out(self, user_email: str, entered_by: str,
                  reporting_type: str, detail: str, user_permission: int,
                  user_company_id: str) -> RC:
        """Updates an existing timestamp with punch-out information.

        Retrieves the latest punch-in timestamp for the user and updates it 
        with the current time and provided details.

        Args:
            user_email (str): The email of the user punching out.
            entered_by (str): The email of the user recording the punch-out.
            reporting_type (str): The type of reporting for the timestamp.
            detail (str): Additional details about the punch-out.
            user_permission (int):  The permission level of the user making the request.
            user_company_id (str): The company ID of the user.

        Returns:
            RC: An RC object indicating success or failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee() and entered_by != user_email:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        user: User | RC = self.user_repository.get_user_by_email(email=user_email)
        if isinstance(user, RC):
            return user

        if perm.is_employer() and user_company_id != user.company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        timestamps: list[TimeStamp] = self.timestamp_repository.get_range(start_of_day, end_of_day, user_email)
        timestamp: TimeStamp = None
        if len(timestamps):
            for ts in timestamps:
                if ts.punch_out_timestamp is None:
                    timestamp = ts
                    break
                
        if timestamp:
            timestamp.punch_out_timestamp = datetime.now(timezone.utc)
            timestamp.reporting_type = reporting_type
            timestamp.detail = detail
            
            return self._update(self.timestamp_repository, timestamp)
        else:
            return RC(E_RC.RC_INVALID_INPUT, 'No punch-in found for today. Please manually add a punch-in entry.\naction_required manual_punch_in')

    def edit_timestamp(self, timestamp_uuid: str, punch_in_timestamp_str: str,
                       punch_out_timestamp_str: str, punch_type: int,
                       detail: str, reporting_type: str,
                       current_user_email: str, user_permission: int,
                       user_company_id: str) -> RC:

        """Edits an existing timestamp record.
        Allows updating various fields of the timestamp and performs
        authorization checks to ensure only authorized users can edit.

        Args:
            timestamp_uuid (str): The UUID of the timestamp to edit.
            punch_in_timestamp_str (str): ISO formatted string for the new punch-in time.
            punch_out_timestamp_str (str): ISO formatted string for the new punch-out time.
            punch_type (int): The new punch type.
            detail (str): The new detail string.
            reporting_type (str): The new reporting type.
            current_user_email (str): The email of the user making the edit request.
            user_permission (int): The permission level of the user making the request.
            user_company_id (str): The company ID of the user.

        Returns:
            RC: An RC object indicating success or failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        timestamp: TimeStamp | RC = self.timestamp_repository.get_timestamp_by_uuid(timestamp_uuid)
        if isinstance(timestamp, RC):
            return timestamp

        elif perm.is_employer():
            if str(timestamp.user.company_id) != user_company_id:
                return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')
        elif perm.is_employee():
            if current_user_email != timestamp.user_email:
                return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        if punch_in_timestamp_str:
            punch_in_timestamp = self._iso_str_to_utc_datetime(punch_in_timestamp_str)
            if isinstance(punch_in_timestamp, RC):
                return punch_in_timestamp
            timestamp.punch_in_timestamp = punch_in_timestamp
            
        if punch_out_timestamp_str:
            punch_out_timestamp = self._iso_str_to_utc_datetime(punch_out_timestamp_str)
            if isinstance(punch_out_timestamp, RC):
                return punch_out_timestamp
            timestamp.punch_out_timestamp = punch_out_timestamp
            
        if punch_type:
            timestamp.punch_type = punch_type
        if detail:
            timestamp.detail = detail
        if reporting_type:
            timestamp.reporting_type = reporting_type

        timestamp.entered_by = current_user_email
        
        return self._update(self.timestamp_repository, timestamp)

    def delete_timestamp(self, uuid: str, current_user_email: str,
                         user_permission: int, user_company_id: str) -> RC:
        """Deletes a timestamp record.

        Retrieves the timestamp by its UUID and performs authorization checks
        before deleting it from the repository.

        Args:
            uuid (str): The UUID of the timestamp to delete.
            current_user_email (str): The email of the user requesting the deletion.
            user_permission (int): The permission level of the user making the request.
            user_company_id (str): The company ID of the user.

        Returns:
            RC: An RC object indicating success or failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        timestamp: TimeStamp | RC = self.timestamp_repository.get_timestamp_by_uuid(uuid)
        if isinstance(timestamp, RC):
            return timestamp

        if not timestamp:
            return RC(E_RC.RC_NOT_FOUND, 'Timestamp not found')

        if perm.is_employee() and current_user_email != timestamp.user.email:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')
        if perm.is_employer() and user_company_id != timestamp.user.company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        return self._delete(self.timestamp_repository, timestamp)

    def get_timestamps_range(self, user_email: str, start_date_str: str,
                             end_date_str: str, current_user_email: str,
                             user_permission: int,
                             user_company_id: str) -> list | RC:
        """Retrieves timestamps within a specific date range.

        Performs authorization checks and returns a list of timestamps within 
        the given range for the specified user.

        Args:
            user_email (str): The email of the user for whom to retrieve timestamps.
            start_date_str (str): ISO formatted string representing the start date.
            end_date_str (str): ISO formatted string representing the end date.
            current_user_email (str): The email of the user making the request.
            user_permission (int): The permission level of the user making the request.
            user_company_id (str): The company ID of the user.

        Returns:
            list | RC: A list of timestamps (as dictionaries) or an RC object indicating failure.
        """
        if not user_email or not start_date_str or not end_date_str:
                return RC(E_RC.RC_INVALID_INPUT, 'Missing start_date or end_date')
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm

        requested_user: User | RC = self.user_repository.get_user_by_email(email=user_email)
        if isinstance(requested_user, RC):
            return requested_user

        if perm.is_employer() and (str(requested_user.company_id) != user_company_id):
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')
            
        elif perm.is_employee() and (current_user_email != user_email):
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        start_date = self._iso_str_to_utc_datetime(start_date_str)
        end_date = self._iso_str_to_utc_datetime(end_date_str)
        if isinstance(start_date, RC) or isinstance(end_date, RC):
            return start_date
        
        if end_date < start_date:
                return RC(E_RC.RC_INVALID_INPUT, 'Start date must earlier than end date')
        
        timestamps = self.timestamp_repository.get_range(start_date, end_date, requested_user.email)
        if isinstance(timestamps, RC):
            return timestamps
            
        return [timestamp.to_dict() for timestamp in timestamps]

    def check_punch_in_status(self, user_email: str, current_user_email ,user_permission: int,
                              user_company_id: str) -> bool | RC:
        """Checks if a user is currently punched in.

        Retrieves the latest timestamp for the user and checks if it has a punch_out_timestamp.

        Args:
            user_email (str): The email of the user to check.
            current_user_email (str): The email of the user making the request.
            user_permission (int): The permission level of the user making the request.
            user_company_id (str): The company ID of the user.

        Returns:
            bool | RC: True if the user is punched in, False otherwise, or an RC object indicating failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee() and user_email != current_user_email:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        user: User | RC = self.user_repository.get_user_by_email(email=user_email)
        if isinstance(user, RC):
            return user

        if perm.is_employer() and user_company_id != user.company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
            
        timestamp: TimeStamp | RC = self.timestamp_repository.check_punch_in_status(user_email, start_of_day, end_of_day)
        if isinstance(timestamp, RC):
            return timestamp
        
        if timestamp:
            return True
        else:
            return False
        
    def get_all_timestamps(self, user_permission: int) -> list | RC:
        """Retrieves all timestamp records.

        Performs authorization checks and returns a list of all timestamps in the repository.

        Args:
            user_permission (int): The permission level of the user making the request.

        Returns:
            list | RC: A list of all timestamps (as dictionaries), or an RC object indicating failure.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

        timestamps = self.timestamp_repository.get_all_timestamps()
        return [timestamp.to_dict() for timestamp in timestamps]
    

    def _iso_str_to_utc_datetime(self, date_str: str):
        """Converts an ISO formatted date string to a datetime object in UTC timezone.

        Handles potential ValueError exceptions during the conversion.

        Args:
            date_str (str): The date string to convert.

        Returns:
            datetime | RC: A datetime object in UTC timezone, or an RC object indicating an error.
        """
        try:
            if date_str and not isinstance(date_str, datetime):
                return iso2datetime(date_str)
            else:
                return date_str
            
        except ValueError:
            return RC(E_RC.RC_INVALID_INPUT, 'Invalid punch_in_timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)')
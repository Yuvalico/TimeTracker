from models import *
from typing import List
from cmn_utils import print_exception
from datetime import datetime
from classes.domainclasses.TimeStamp import TimeStamp
from classes.utilities.RC import RC, E_RC
from classes.repositories.BaseRepository import BaseRepository


class TimeStampRepository(BaseRepository):
    """
    A repository class for managing timestamps in the database.

    This class provides methods for accessing and manipulating timestamp data 
    in the database using SQLAlchemy.

    Methods:
        get_all_timestamps(self) -> List[TimeStamp]: Retrieves all timestamps.
        get_timestamp_by_uuid(self, uuid: str) -> TimeStamp|RC: Retrieves a timestamp by its UUID.
        check_punch_in_status(self, email: str, start_of_day: datetime, end_of_day: datetime) -> bool|RC|None: 
            Checks if a user is currently punched in within a given time range.
        get_range(self, start_date: datetime, end_date: datetime, email: str = None, company_id: str = None) -> list|RC: 
            Retrieves timestamps within a given date range, optionally filtered by email or company ID.
    """
    def __init__(self, db: SQLAlchemy):
        """
        Initializes the TimeStampRepository with a SQLAlchemy database instance.

        Args:
            db (SQLAlchemy): The SQLAlchemy database instance.
        """
        super().__init__(db)

    def get_all_timestamps(self) -> List[TimeStamp]:
        """
        Retrieves all timestamps from the database.

        Returns:
            List[TimeStamp]: A list of all timestamps.
        """
        timestamps = TimeStampModel.query.all()
        return [timestamp.to_class() for timestamp in timestamps]

    def get_timestamp_by_uuid(self, uuid: str) -> TimeStamp|RC:
        """
        Retrieves a timestamp by its UUID.

        Args:
            uuid (str): The UUID of the timestamp.

        Returns:
            TimeStamp|RC: The TimeStamp object if found, otherwise an RC object indicating an error.
        """
        timestamp = TimeStampModel.query.get(uuid)
        if timestamp:
            return timestamp.to_class()
        return RC(E_RC.RC_NOT_FOUND, "Time stamp not found")
    
        
    def check_punch_in_status(self, email: str, start_of_day: datetime, end_of_day: datetime) -> bool|RC|None:
        """
        Checks if a user is currently punched in within a given time range.

        This method checks if there is an open timestamp (punch-in without a corresponding punch-out)
        for the given user email within the specified date range.

        Args:
            email (str): The email of the user.
            start_of_day (datetime): The start of the date range.
            end_of_day (datetime): The end of the date range.

        Returns:
            bool|RC|None: True if the user is punched in, False if not, 
                          an RC object in case of an error, or None if no timestamp is found.
        """
        try:
            
            timestamp: TimeStampModel = TimeStampModel.query.filter(
                TimeStampModel.user_email == email,
                TimeStampModel.punch_in_timestamp >= start_of_day,
                TimeStampModel.punch_in_timestamp <= end_of_day,
                TimeStampModel.punch_out_timestamp == None
            ).order_by(TimeStampModel.punch_in_timestamp.desc()).first()

            if timestamp:
                return timestamp.to_class()
            else:
                return None
                
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def get_range(self, start_date: datetime, end_date: datetime, email: str = None, company_id: str = None) -> list|RC:
        """
        Retrieves timestamps within a given date range, optionally filtered by email or company ID.

        Args:
            start_date (datetime): The start of the date range.
            end_date (datetime): The end of the date range.
            email (str, optional): The email of the user to filter by. Defaults to None.
            company_id (str, optional): The ID of the company to filter by. Defaults to None.

        Returns:
            list|RC: A list of TimeStamp objects within the date range, 
                     or an RC object indicating an error.
        """
        try:
            
            if company_id is None:
                timestamps: TimeStampModel= TimeStampModel.query.filter(
                    TimeStampModel.user_email == email,
                    TimeStampModel.punch_in_timestamp >= start_date,
                    TimeStampModel.punch_in_timestamp <= end_date
                ).all()
            elif company_id is not None:
                timestamps: TimeStampModel= TimeStampModel.query.filter(TimeStampModel.punch_in_timestamp >= start_date,
                            TimeStampModel.punch_in_timestamp <= end_date).join(UserModel, TimeStampModel.user_email == UserModel.email)\
                            .filter(UserModel.company_id == company_id).all()
                
            return [timestamp.to_class() for timestamp in timestamps]
                
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
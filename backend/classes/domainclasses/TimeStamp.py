from datetime import datetime
from classes.domainclasses.User import User
from cmn_utils import *
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from classes.domainclasses.DomainClassInterface import DomainClassInterface


@dataclass
class TimeStamp(DomainClassInterface):
    """
    Represents a timestamp entry for tracking work hours.

    Attributes:
        user_email (str): The email address of the user associated with the timestamp.
        entered_by (str): The identifier of the user who entered the timestamp.
        punch_type (int): The type of punch (e.g., clock-in, clock-out, break).
        punch_in_timestamp (datetime): The date and time of the punch-in event.
        detail (str): Additional details or notes related to the timestamp.
        reporting_type (str): The type of reporting associated with the timestamp.
        punch_out_timestamp (datetime, optional): The date and time of the punch-out event.
        uuid (str, optional): A unique identifier for the timestamp entry.
        total_work_time (int, optional): The total work time calculated from the timestamps.
        last_update (datetime, optional): The date and time of the last update to the timestamp.
        user (User, optional): The User object associated with the timestamp.

    Methods:
        to_dict(self): Converts the TimeStamp object to a dictionary representation.
        to_model(self): Converts the TimeStamp object to a TimeStampModel instance.
    """
    user_email: str
    entered_by: str
    punch_type: int
    punch_in_timestamp: datetime
    detail: str
    reporting_type: str
    punch_out_timestamp: datetime = None
    uuid: str = None
    total_work_time: int = None
    last_update: datetime = None
    user: User = None

    def to_dict(self):
        """
        Converts the TimeStamp object to a dictionary.

        Returns:
            dict: A dictionary representation of the TimeStamp object.
        """
        return {
            'uuid': str(self.uuid),
            'user_email': str(self.user_email),
            'entered_by': str(self.entered_by),
            'punch_type': self.punch_type,
            'punch_in_timestamp': datetime2iso(self.punch_in_timestamp),
            'punch_out_timestamp': datetime2iso(self.punch_out_timestamp),
            'reporting_type': self.reporting_type,
            'detail': self.detail,
            'total_work_time': self.total_work_time,
            'last_update': datetime2iso(self.last_update),
        }
        
    def to_model(self):
        """
        Converts the TimeStamp object to a TimeStampModel instance.

        Returns:
            TimeStampModel: A TimeStampModel instance representing the timestamp.
        """
        from models import TimeStampModel
        return TimeStampModel(
            uuid =  self.uuid if self.uuid else None,
            user_email =  self.user_email,
            entered_by =  self.entered_by,
            punch_type =  self.punch_type,
            punch_in_timestamp =  iso2datetime(self.punch_in_timestamp) if not isinstance(self.punch_in_timestamp, datetime) else self.punch_in_timestamp,
            punch_out_timestamp =  iso2datetime(self.punch_out_timestamp) if not isinstance(self.punch_out_timestamp, datetime) else self.punch_out_timestamp,
            reporting_type =  self.reporting_type,
            detail =  self.detail,
            last_update =  self.last_update,
        )

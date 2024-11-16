from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime
from sqlalchemy.sql import expression
from sqlalchemy.ext.hybrid import hybrid_property
from classes.domainclasses.User import User
from classes.domainclasses.Company import Company
from classes.domainclasses.TimeStamp import TimeStamp
from abc import abstractmethod

db = SQLAlchemy()
class ModelInterface():
    """
    An interface for database models.

    Defines an abstract method `to_class` that should be implemented by 
    concrete model classes to convert database model objects to domain objects.
    """
    @abstractmethod
    def to_class(self):
        raise NotImplementedError
    
class CompanyModel(db.Model, ModelInterface):
    """
    Database model for companies.

    Represents companies in the database, storing their ID, name, and active status.
    Also defines a relationship with the `UserModel` for users belonging to the company.

    Attributes:
        company_id (UUID): Primary key, automatically generated UUID.
        company_name (str): Name of the company.
        is_active (bool): Indicates if the company is active.
        users (relationship): Relationship with `UserModel` for users in the company.
    """
    __tablename__ = 'companies'
    company_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    company_name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    users = db.relationship('UserModel', backref='company')

    def to_class(self):
        """Converts a `CompanyModel` object to a `Company` domain object."""
        return Company(
            company_id=str(self.company_id),
            company_name=self.company_name,
            is_active=self.is_active
        )

class UserModel(db.Model, ModelInterface):
    """
    Database model for users.

    Represents users in the database, storing their email, name, contact details,
    company affiliation, role, permissions, password hash, and employment information.

    Attributes:
        email (str): Primary key, email address of the user.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        mobile_phone (str): Mobile phone number of the user.
        company_id (UUID): Foreign key referencing `CompanyModel`.
        role (str): Role of the user in the company.
        permission (int): Permission level of the user.
        pass_hash (str): Hashed password of the user.
        is_active (bool): Indicates if the user account is active.
        salary (float): Salary of the user.
        work_capacity (float): Daily work capacity of the user in hours.
        employment_start (datetime): Employment start date.
        employment_end (datetime): Employment end date (if applicable).
        weekend_choice (str): User's preferred weekend days.
    """
    __tablename__ = 'users'
    email = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    mobile_phone = db.Column(db.String(11))
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('companies.company_id'))
    role = db.Column(db.String(255))
    permission = db.Column(db.Integer)
    pass_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    salary = db.Column(db.Numeric)
    work_capacity = db.Column(db.Numeric)
    employment_start = db.Column(db.DateTime(timezone=True))
    employment_end = db.Column(db.DateTime(timezone=True))
    weekend_choice = db.Column(db.String(64))

    def to_class(self):
        """Converts a `UserModel` object to a `User` domain object."""
        return User(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            mobile_phone=self.mobile_phone,
            company_id=str(self.company_id),  
            role=self.role,
            permission=self.permission,
            pass_hash=self.pass_hash,
            is_active=self.is_active,
            salary=float(self.salary) if self.salary is not None else None,
            work_capacity=float(self.work_capacity) if self.work_capacity is not None else None,
            employment_start=self.employment_start,
            employment_end=self.employment_end,
            weekend_choice=self.weekend_choice,
            company=self.company.to_class(),
        )
        
class TimeStampModel(db.Model, ModelInterface):
    """
    Database model for timestamps.

    Represents timestamps recorded by users, storing information about the user,
    punch type, timestamps, reporting type, details, and calculated total work time.

    Attributes:
        uuid (UUID): Primary key, automatically generated UUID.
        user_email (str): Foreign key referencing `UserModel`.
        entered_by (str): Foreign key referencing `UserModel` (who entered the timestamp).
        punch_type (int): Type of punch (e.g., start work, start break).
        punch_in_timestamp (datetime): Timestamp for punch-in.
        punch_out_timestamp (datetime): Timestamp for punch-out.
        reporting_type (str): Type of reporting (e.g., work, vacation).
        detail (str): Additional details about the timestamp.
        total_work_time (int): Calculated total work time in seconds (hybrid property).
        last_update (datetime): Timestamp of the last update to the record.
        entered_by_user (relationship): Relationship with `UserModel` for who entered the timestamp.
        user (relationship): Relationship with `UserModel` for the user the timestamp belongs to.
    """
    __tablename__ = 'time_stamps'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_email = db.Column(db.ForeignKey('users.email'),nullable=False)
    entered_by = db.Column(db.ForeignKey('users.email'), nullable=False)
    punch_type = db.Column(db.Integer)
    punch_in_timestamp = db.Column(db.DateTime(timezone=True))
    punch_out_timestamp = db.Column(db.DateTime(timezone=True))
    reporting_type = db.Column(db.String(32))
    detail = db.Column(db.String(255))
    total_work_time = db.Column(db.Integer, nullable=True) 
    last_update = db.Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=expression.text('CURRENT_TIMESTAMP AT TIME ZONE \'UTC\'')
    )

    entered_by_user = db.relationship(
        'UserModel',
        foreign_keys=[entered_by],
        backref='entered_timestamps'
    )

    user = db.relationship(
        'UserModel',
        foreign_keys=[user_email],
        backref='timestamps'  
    )

    @hybrid_property
    def total_work_time(self):
        """Calculates the total work time in seconds between punch-in and punch-out timestamps."""
        if self.punch_out_timestamp and self.punch_in_timestamp:
            time_diff = self.punch_out_timestamp - self.punch_in_timestamp
            return int(time_diff.total_seconds()) 
        return None 

    def to_class(self):
        """Converts a `TimeStampModel` object to a `TimeStamp` domain object."""
        return TimeStamp(
            uuid=str(self.uuid),
            user_email=self.user_email,
            entered_by=self.entered_by,
            punch_type=self.punch_type,
            punch_in_timestamp=self.punch_in_timestamp,
            punch_out_timestamp=self.punch_out_timestamp,
            reporting_type=self.reporting_type,
            detail=self.detail,
            total_work_time=self.total_work_time,
            last_update=self.last_update,
            user = self.user.to_class()
        )

from classes.utilities.RC import RC
from classes.utilities.RC import E_RC
from enum import IntEnum

class E_PERMISSIONS(IntEnum):
    """
    Enum representing different permission levels in the system.

    Provides methods for converting between enum members, their values, and string representations.

    Members:
        net_admin (int): Highest permission level, typically for system administrators.
        employer (int): Permission level for employers/managers.
        employee (int): Permission level for regular employees.

    Methods:
        __call__(self, value): Attempts to convert a value to an E_PERMISSIONS member.
        to_str(self): Returns the string representation of the enum member.
        to_enum(value): Converts a value to its corresponding enum member.
    """
    net_admin = 0
    employer = 1
    employee = 2
    
    def __call__(self, value):
        """
        Attempts to convert a value to an E_PERMISSIONS member.

        Args:
            value: The value to convert.

        Returns:
            E_PERMISSIONS | str: The corresponding E_PERMISSIONS member if successful, 
                                 otherwise returns "Invalid Permission".
        """
        try:
            return E_PERMISSIONS(int(value))  
        except ValueError:
            return "Invalid Permission"

    def to_str(self):
        """
        Returns a string representation of the enum member.
        """
        try:
            return self.name 
        
        except Exception as e:
            return "unknown"
        
    @staticmethod
    def to_enum(value):
        """
        Converts a value to its corresponding enum member.

        Args:
            value: The value to convert.

        Returns:
            MyEnum or None: The enum member with the matching value, or None if not found.
        """
        for member in E_PERMISSIONS:
            if member.value == int(value):
                return member
        return RC(E_RC.RC_INVALID_INPUT, f"Invalid permission level {value}")
    
class Permission():
    """
    A class for managing and checking user permissions.

    Uses the E_PERMISSIONS enum to represent different permission levels.

    Methods:
        is_net_admin(self) -> bool: Checks if the permission is net_admin.
        is_employer(self) -> bool: Checks if the permission is employer.
        is_employee(self) -> bool: Checks if the permission is employee.
    """
    def __init__(self, permission: E_PERMISSIONS):
        """
        Initializes a Permission object.

        Args:
            permission (E_PERMISSIONS): The permission level to assign to the object.
        """
        self.permission = permission
    
    def is_net_admin(self) -> bool:
        """Checks if the permission is net_admin."""
        return self.permission == E_PERMISSIONS.net_admin

    def is_employer(self) -> bool:
        """Checks if the permission is employer."""


    def is_employee(self) -> bool:
        """Checks if the permission is employee."""
        return self.permission == E_PERMISSIONS.employee
    
    
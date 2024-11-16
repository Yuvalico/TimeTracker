from enum import IntEnum
from flask import jsonify
class E_RC(IntEnum):
    """
    Enum for standard return codes used in the application.

    These codes represent common HTTP status codes and application-specific error conditions.

    Members:
        RC_OK (int): Successful operation (HTTP 200 OK).
        RC_SUCCESS (int): Resource created successfully (HTTP 201 Created).
        RC_ERROR_DATABASE (int): Internal server error related to database operations (HTTP 500 Internal Server Error).
        RC_NOT_FOUND (int): Resource not found (HTTP 404 Not Found).
        RC_UNAUTHORIZED (int): Unauthorized access (HTTP 403 Forbidden).
        RC_INVALID_INPUT (int): Invalid input provided (HTTP 422 Unprocessable Entity).
    """
    RC_OK = 200
    RC_SUCCESS = 201
    RC_ERROR_DATABASE = 500
    RC_NOT_FOUND = 404
    RC_UNAUTHORIZED = 403
    RC_INVALID_INPUT = 422
    
class RC:
    """
    Return Code class to encapsulate return codes and their descriptions.

    This class helps standardize error handling and response formatting in the application.

    Methods:
        __init__(self, code: int, description: str): Initializes an RC object.
        __str__(self): Returns a string representation of the RC object.
        __repr__(self): Returns a string representation of the RC object.
        to_dict(self): Converts the RC object to a dictionary.
        is_ok(self): Checks if the return code indicates success.
        to_json(self): Converts the RC object to a JSON response with appropriate HTTP status code.
    """
    def __init__(self, code: int, description: str):
        """
        Initializes an RC object.

        Args:
            code (int): The return code (typically from the E_RC enum).
            description (str): A descriptive message associated with the return code.
        """
        self.code = code
        self.description = description

    def __str__(self):
        """Returns a string representation of the RC object."""
        return f"{self.description}"

    def __repr__(self):
        """Returns a string representation of the RC object."""
        return self.__str__()

    def to_dict(self):
        """Converts the RC object to a dictionary."""
        return {
            "code": self.code,
            "description": self.description,
        }
    
    def is_ok(self):
        """Checks if the return code indicates success."""
        if self.code == E_RC.RC_OK or self.code == E_RC.RC_SUCCESS:
            return True
        else:
            return False
          
    def to_json(self):
        """
        Converts the RC object to a JSON response.

        Includes the description as either a "message" (for success) or an "error" (for failure),
        along with the appropriate HTTP status code.
        """
        if self.is_ok():
            msg = "message"
        else:
            msg = "error"
        
        print(f"{msg}: {self.description}")
        return jsonify({f"{msg}": self.description}), self.code

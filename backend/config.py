import os
from dotenv import load_dotenv

load_dotenv()  
class Config:
    """
    Configuration class for the application.

    Loads environment variables from a .env file and provides default values if not found.

    Attributes:
        JWT_SECRET_KEY (str): Secret key for JWT token generation.
        DB_HOST (str): Hostname of the database server.
        DB_PORT (str): Port number of the database server.
        DB_NAME (str): Name of the database.
        DB_USER (str): Username for database connection.
        DB_PASSWORD (str): Password for database connection.
        WEB_URL (str): URL of the web application.
        WEB_PORT (str): Port number of the web application.
    """
    JWT_SECRET_KEY  = os.getenv('JWT_SECRET', 'your_jwt_secret_key')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'Name')
    DB_USER = os.getenv('DB_USER', 'User')
    DB_PASSWORD = os.getenv('DB_PASS', 'pass')

    WEB_URL = os.getenv('WEB_URL', 'localhost')
    WEB_PORT = os.getenv('WEB_PORT', '5173')
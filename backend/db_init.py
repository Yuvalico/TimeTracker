from models import CompanyModel, UserModel
from sqlalchemy import text  
from sqlalchemy_utils import database_exists, create_database
from config import *
import bcrypt
from datetime import datetime, timezone
from classes.utilities.Permission import E_PERMISSIONS
import random



def create_db(app, db):
    """
    Creates the database and populates it with initial data.

    This function checks if the database exists, creates it if necessary, 
    and then populates it with the following:
        - Enables the `uuid-ossp` extension for UUID generation.
        - Creates all tables defined in the `models` module.
        - Creates a default `NetAdmin Company` and a `net admin` user.
        - Creates two test companies (`tlv300`, `test1`) with corresponding employer and employee users.

    Args:
        app: The Flask application instance.
        db: The SQLAlchemy database object.
    """
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if not database_exists(db_uri):
        print(f"Database '{Config.DB_NAME}' not found. Creating...")
        create_database(db_uri)  
        print(f"Database '{Config.DB_NAME}' created successfully.")

    with app.app_context():
        engine = db.get_engine()

        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()  

        db.create_all()  
        print("Tables created successfully.")

        if not CompanyModel.query.filter_by(company_name="NetAdmin Company").first():
            print("Creating NetAdmin company...")
            company = CompanyModel(company_name="NetAdmin Company")
            db.session.add(company)
            db.session.commit()
            print("NetAdmin company created successfully.")
        else:
            print("NetAdmin company already exists.")

        if not UserModel.query.filter_by(email='a@gmail.com').first():
            print("Creating net admin user...")

            company: CompanyModel = CompanyModel.query.filter_by(company_name="NetAdmin Company").first()

            net_admin = UserModel(
                email='a@gmail.com',
                first_name='Net',
                last_name='Admin',
                company_id=company.company_id,  
                role='Net Admin',
                permission=E_PERMISSIONS.net_admin,  
                pass_hash=bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True,
                salary = 1,
                work_capacity = 9,
                employment_start = datetime.now(timezone.utc),
                weekend_choice = "Friday,Saturday"
            )
            db.session.add(net_admin)
            db.session.commit()
            print("Net admin user created successfully.")
        else:
            print("Net admin user already exists.")

        ############ create test data #####################
        company_names = ['tlv300', 'test1']
        companies = []
        for company_name in company_names:
            company = CompanyModel.query.filter_by(company_name=company_name).first()
            if not company:
                company = CompanyModel(company_name=company_name)
                db.session.add(company)
                companies.append(company)
                print(f"{company_name} created successfully.")
        db.session.commit()

        for company in companies:
            employer: UserModel = UserModel.query.filter_by(email=f'{company.company_name}_employer@example.com').first()
            if not employer:
                employer = UserModel(
                    email=f'employer@{company.company_name}.com',
                    first_name='Employer',
                    last_name=company.company_name,
                    mobile_phone = "0123456789",
                    company_id=company.company_id,
                    role='Manager',
                    permission=E_PERMISSIONS.employer, 
                    pass_hash=bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_active=True,
                    salary = random.randint(1, 50) ,
                    work_capacity = random.randint(1, 9) ,
                    employment_start = datetime.now(timezone.utc),
                    weekend_choice = "Friday,Saturday"
                    )
                db.session.add(employer) 
                print(f"{company.company_name} employer created successfully.")

            employee: UserModel = UserModel.query.filter_by(email=f'{company.company_name}_employee@example.com').first()
            if not employee:
                employee = UserModel(
                    email=f'employee@{company.company_name}.com',
                    first_name='Employee',
                    last_name=company.company_name,
                    mobile_phone = "0123456789",
                    company_id=company.company_id,
                    role='secretary',
                    permission=E_PERMISSIONS.employee,  
                    pass_hash=bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_active=True,
                    salary = random.randint(1, 50) ,
                    work_capacity = random.randint(1, 9) ,
                    employment_start = datetime.now(timezone.utc),
                    weekend_choice = "Saturday,Sunday"
                )
                db.session.add(employee)
                print(f"{company.company_name} employee created successfully.")
            db.session.commit()

        engine.dispose()
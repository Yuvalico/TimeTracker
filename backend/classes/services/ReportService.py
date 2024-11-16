from classes.domainclasses.Company import Company
from classes.domainclasses.User import User
from classes.domainclasses.TimeStamp import TimeStamp
from classes.repositories.CompanyRepository import CompanyRepository
from classes.repositories.UserRepository import UserRepository
from classes.repositories.TimeStampRepository import TimeStampRepository
from classes.utilities.Permission import Permission
from classes.services.BaseServiceClass import BaseService
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.utilities.RC import RC, E_RC
from cmn_utils import *
from datetime import datetime, timezone, timedelta
import calendar


class ReportService(BaseService):
    from classes.domainclasses.Company import Company
from classes.domainclasses.User import User
from classes.domainclasses.TimeStamp import TimeStamp
from classes.repositories.CompanyRepository import CompanyRepository
from classes.repositories.UserRepository import UserRepository
from classes.repositories.TimeStampRepository import TimeStampRepository
from classes.utilities.Permission import Permission
from classes.services.BaseServiceClass import BaseService
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.utilities.RC import RC, E_RC
from cmn_utils import *
from datetime import datetime, timezone, timedelta
import calendar


class ReportService(BaseService):
    """
    A service class for generating various reports related to users, companies, and timestamps.

    This class provides methods to generate reports for individual users, company summaries, 
    and company overview reports. It handles date range calculations, data retrieval from 
    repositories, and formatting of report data. It also includes authorization checks 
    to ensure that users can only access reports they are permitted to see.

    Methods:
        user_report(self, user_email, date_range_type, selected_year, selected_month, start_date_str, 
                    end_date_str, user_permission: int, user_company_id: str, current_user_email: str) -> dict | RC: 
                    Generates a report for a specific user.
                    
        company_summary(self, company_id: str, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, 
                        end_date_str: str, user_permission: int, user_company_id: str) -> dict|RC: 
                        Generates a summary report for a specific company.
                        
        company_overview(self, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, 
                        end_date_str: str, user_permission: int) -> dict| RC: 
                        Generates an overview report for all companies.

        _calculate_work_days(self, user: User, time_stamps: list[TimeStamp], start_date: datetime, end_date: datetime) -> tuple: 
                        Calculates the number of days worked, paid days off, unpaid days off, and other relevant metrics for a user within a date range.

        _generate_report_entry(self, user: User, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, 
                                potential_work_days, start_date, end_date, daily_breakdown = None) -> dict|RC: 
                                Generates a report entry for a user, including their work details and calculated salary.

        _set_dates_range(self, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, end_date_str: str) -> tuple|RC: 
                        Sets the start and end dates for the report based on the selected date range type.

        _calculate_salary(self, total_hours_worked: float|str, salary: float|str) -> float: 
                        Calculates the salary for a user based on their total hours worked and hourly salary.
    """
    def __init__(self, user_repository: UserRepository, timestamp_repository: TimeStampRepository, company_repository: CompanyRepository, validator: ModelValidator, factory: DomainClassFactory):
        """
        Initializes the ReportService with necessary dependencies.

        Args:
            user_repository (UserRepository): An instance of the UserRepository for user data access.
            timestamp_repository (TimeStampRepository): An instance of the TimeStampRepository for timestamp data access.
            company_repository (CompanyRepository): An instance of the CompanyRepository for company data access.
            validator (ModelValidator): An instance of the ModelValidator for data validation.
            factory (DomainClassFactory): An instance of the DomainClassFactory for creating domain objects.
        """
        super().__init__(validator, factory)
        self.user_repository: UserRepository = user_repository
        self.timestamp_repository: TimeStampRepository = timestamp_repository
        self.company_repository: CompanyRepository = company_repository

    def user_report(self, user_email, date_range_type, selected_year, selected_month, start_date_str, \
            end_date_str, user_permission: int, user_company_id: str, current_user_email: str) -> dict | RC:
        """
        Generates a report for a specific user.

        This method retrieves user data, timestamps within a specified date range, and calculates 
        work-related metrics such as days worked, paid/unpaid days off, and total hours worked. 
        It then generates a report entry with this information, including a daily breakdown of hours worked.

        Args:
            user_email: The email of the user for whom the report is generated.
            date_range_type: The type of date range selection ('monthly' or 'custom').
            selected_year: The year selected for the report (if date_range_type is 'monthly').
            selected_month: The month selected for the report (if date_range_type is 'monthly').
            start_date_str: The start date of the custom date range (if date_range_type is 'custom').
            end_date_str: The end date of the custom date range (if date_range_type is 'custom').
            user_permission (int): The permission level of the user initiating the request.
            user_company_id (str): The company ID of the user initiating the request.
            current_user_email (str): The email of the currently logged-in user.

        Returns:
            dict | RC: A dictionary containing the user report data if successful, 
                      otherwise an RC object indicating an error.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee() and user_email and user_email != current_user_email:
             return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
         
        result = self._set_dates_range(date_range_type, selected_year, selected_month, start_date_str, end_date_str)
        if isinstance(result, RC):
            return result
        
        start_date, end_date = result

        user: User = self.user_repository.get_user_by_email(user_email)
        if isinstance (user, RC):
            return user
        
        if perm.is_employer() and (str(user.company_id) != str(user_company_id)):
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        time_stamps = self.timestamp_repository.get_range(start_date, end_date, user_email)
        if isinstance(time_stamps, RC):
            return time_stamps

        days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked,\
            potential_work_days, daily_breakdown = self._calculate_work_days(user, time_stamps, start_date, end_date)

        report_entry: dict = self._generate_report_entry(user, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date, daily_breakdown)

        return report_entry

    def company_summary(self, company_id: str, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, \
                end_date_str: str, user_permission: int, user_company_id: str) -> dict|RC:
        """
        Generates a summary report for a specific company.

        This method retrieves all users belonging to the specified company and generates a report 
        for each user, including details like days worked, paid/unpaid days off, total hours worked, 
        and potential workdays within the given date range. It aggregates these individual user reports 
        into a comprehensive company summary report.

        Args:
            company_id (str): The ID of the company for which to generate the report.
            date_range_type (str): The type of date range selection ('monthly' or 'custom').
            selected_year (str): The year selected for the report (if date_range_type is 'monthly').
            selected_month (str): The month selected for the report (if date_range_type is 'monthly').
            start_date_str (str): The start date of the custom date range (if date_range_type is 'custom').
            end_date_str (str): The end date of the custom date range (if date_range_type is 'custom').
            user_permission (int): The permission level of the user initiating the request.
            user_company_id (str): The company ID of the user initiating the request.

        Returns:
            dict|RC: A dictionary containing the company summary report data if successful, 
                    otherwise an RC object indicating an error.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        if perm.is_employer() and (str(user_company_id) != str(company_id)):
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        result = self._set_dates_range(date_range_type, selected_year, selected_month, start_date_str, end_date_str)
        if isinstance(result, RC):
            return result
        
        start_date, end_date = result
        
        users: list[User] = self.company_repository.get_company_users(company_id=company_id)
        report = []
        for user in users:
            timestamps: list[TimeStamp] = self.timestamp_repository.get_range(start_date, end_date, user.email)

            days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, _\
                =self._calculate_work_days(user, timestamps, start_date, end_date)
            
            report_entry: dict = self._generate_report_entry(user, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date)
            report.append(report_entry)

        return report

    def company_overview(self, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, end_date_str: str, user_permission: int) -> dict| RC:
        """
        Generates an overview report for all active companies.

        This method retrieves all active companies and iterates through them to calculate key metrics 
        such as the number of employees, total hours worked by employees, and the total monthly salary 
        paid by each company. It also gathers information about the company administrators. The report 
        provides a high-level summary of company performance and workforce data.

        Args:
            date_range_type (str): The type of date range selection ('monthly' or 'custom').
            selected_year (str): The year selected for the report (if date_range_type is 'monthly').
            selected_month (str): The month selected for the report (if date_range_type is 'monthly').
            start_date_str (str): The start date of the custom date range (if date_range_type is 'custom').
            end_date_str (str): The end date of the custom date range (if date_range_type is 'custom').
            user_permission (int): The permission level of the user initiating the request.

        Returns:
            dict| RC: A dictionary containing the company overview report data if successful, 
                    otherwise an RC object indicating an error.
        """
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        result = self._set_dates_range(date_range_type, selected_year, selected_month, start_date_str, end_date_str)
        if isinstance(result, RC):
            return result
        
        start_date, end_date = result
        
        companies: list[Company] = self.company_repository.get_all_active_companies()
        
        report = []
        for company in companies:
            employees: list[User] = self.company_repository.get_company_users(company_id=company.company_id)
            num_employees = len(employees)
            total_hours_worked = 0
            total_monthly_salary = 0
            monthly_payments = []

            for employee in employees:
                employee_time_stamps = self.timestamp_repository.get_range(start_date, end_date, employee.email)
                employee_hours_worked = 0
                for ts in employee_time_stamps:
                    employee_hours_worked += ts.total_work_time or 0
                
                total_hours_worked += employee_hours_worked

                monthly_payment = self._calculate_salary(total_hours_worked, float(employee.salary or 0))
                total_monthly_salary += monthly_payment
                monthly_payments.append(round(monthly_payment, 2))
            
            admin_users: list[User] = self.company_repository.get_company_admins(company.company_id)
            admin_names = [admin.first_name + " " + admin.last_name for admin in admin_users]
            report.append( {
                "companyName": company.company_name,
                "numEmployees": num_employees,
                "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
                "totalMonthlySalary": round(total_monthly_salary, 2),
                "monthlyPayments": monthly_payments,
                "adminNames": admin_names
            })
            
        return report
        
        
    def _calculate_work_days(self, user: User, time_stamps: list[TimeStamp], start_date: datetime, end_date: datetime) -> tuple:
        """
        Calculates the number of days worked, paid days off, unpaid days off, and other relevant metrics for a user within a date range.

        This method iterates through each day in the given date range and checks the user's timestamps 
        to determine if they worked on that day, took a paid/unpaid day off, or did not report any 
        activity. It also calculates the total hours worked and generates a daily breakdown of hours 
        worked and reporting type.

        Args:
            user (User): The User object for whom to calculate work days.
            time_stamps (list[TimeStamp]): A list of TimeStamp objects representing the user's activity.
            start_date (datetime): The start date of the date range.
            end_date (datetime): The end date of the date range.

        Returns:
            tuple: A tuple containing the following calculated metrics:
                - days_worked: The number of days the user worked.
                - paid_days_off: The number of paid days off taken by the user.
                - unpaid_days_off: The number of unpaid days off taken by the user.
                - days_not_reported: The number of days with no reported activity from the user.
                - total_hours_worked: The total number of hours worked by the user.
                - potential_work_days: The total number of potential workdays in the date range (excluding weekends based on user's preference).
                - daily_breakdown: A list of dictionaries containing a daily breakdown of hours worked and reporting type.
        """
        total_hours_worked = 0
        daily_breakdown = []
        paid_days_off = 0
        unpaid_days_off = 0
        days_not_reported = 0
        days_worked = 0
        potential_work_days = 0
        current_date = start_date

        while current_date <= end_date:
            found_entry = False
            work_type = None
            daily_hours = 0
            if not user.weekend_choice or current_date.strftime('%A').lower() not in map(str.lower, user.weekend_choice.split(',')):  
                potential_work_days += 1
                for ts in time_stamps:
                    if ts.punch_in_timestamp.date() == current_date.date():
                        found_entry = True
                        if ts.reporting_type == "work":
                            work_type = "work"
                            days_worked += 1
                            daily_hours += ts.total_work_time or 0
                            
                        elif ts.reporting_type == 'paidoff':
                            paid_days_off += 1
                            daily_hours = 8 * 3600
                            work_type = ts.reporting_type
                            break
                        elif ts.reporting_type == 'unpaidoff':
                            unpaid_days_off += 1
                            daily_hours = 0
                            work_type = ts.reporting_type
                            break
                        
                        break
                if not found_entry:
                    days_not_reported += 1
                
                total_hours_worked += daily_hours

            daily_breakdown.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "hoursWorked": format_hours_to_hhmm(daily_hours),
                "reportingType": work_type
            })
            current_date += timedelta(days=1)

        return days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, daily_breakdown
    
    def _generate_report_entry(self, user: User, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date, daily_breakdown = None) -> dict|RC:
        """
        Generates a report entry for a user, including their work details and calculated salary.

        This method takes various calculated metrics (days worked, days off, total hours worked, etc.) 
        and user details to construct a comprehensive report entry. It includes information about the 
        user's work activity, potential workdays, total payment required, and a daily breakdown of their hours worked.

        Args:
            user (User): The User object for whom to generate the report entry.
            days_worked: The number of days the user worked.
            paid_days_off: The number of paid days off taken by the user.
            unpaid_days_off: The number of unpaid days off taken by the user.
            days_not_reported: The number of days with no reported activity from the user.
            total_hours_worked: The total number of hours worked by the user.
            potential_work_days: The total number of potential workdays in the date range.
            start_date: The start date of the reporting period.
            end_date: The end date of the reporting period.
            daily_breakdown: A list of dictionaries containing a daily breakdown of hours worked and reporting type.

        Returns:
            dict|RC: A dictionary containing the user's report entry data if successful, 
                    otherwise an RC object indicating an error.
        """
        employee_name = user.first_name + " " + user.last_name
        salary = float(user.salary or 0)
        total_payment_required = self._calculate_salary(total_hours_worked, salary)
        
        report = {
            "employeeName": employee_name,
            "daysWorked": days_worked,
            "paidDaysOff": paid_days_off,        
            "unpaidDaysOff": unpaid_days_off,    
            "daysNotReported": days_not_reported,  
            "potentialWorkDays": potential_work_days, 
            "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
            "workCapacityforRange":format_hours_to_hhmm(calculate_work_capacity(user, start_date, end_date) * 3600),
            "totalPaymentRequired": round(total_payment_required, 2),
            "dailyBreakdown": daily_breakdown,
            "userDetails": {  
                "email": user.email,
                "role": user.role,
                "phone": user.mobile_phone,
                "salary": salary,
                "workCapacity": format_hours_to_hhmm(float(user.work_capacity or 0) * 3600), 
                "weekendChoice": user.weekend_choice
            }
        }
        
        return report
    
    def _set_dates_range(self, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, end_date_str: str)->tuple|RC:
        """
        Sets the start and end dates for the report based on the selected date range type.

        This method handles the logic for determining the appropriate start and end dates for the report. 
        It supports two types of date ranges: 'monthly' and 'custom'. For 'monthly' reports, it calculates 
        the start and end dates of the selected month. For 'custom' reports, it parses the provided start 
        and end date strings.

        Args:
            date_range_type (str): The type of date range selection ('monthly' or 'custom').
            selected_year (str): The year selected for the report (if date_range_type is 'monthly').
            selected_month (str): The month selected for the report (if date_range_type is 'monthly').
            start_date_str (str): The start date of the custom date range (if date_range_type is 'custom').
            end_date_str (str): The end date of the custom date range (if date_range_type is 'custom').

        Returns:
            tuple|RC: A tuple containing the start_date and end_date as datetime objects if successful, 
                    otherwise an RC object indicating an error.
        """
        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return RC(E_RC.RC_INVALID_INPUT, 'Year and month are required for monthly reports')

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
            return start_date, end_date
        
        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return RC(E_RC.RC_INVALID_INPUT, 'Start and end dates are required for custom reports')
            try:
                start_date = iso2datetime(start_date_str)
                end_date = iso2datetime(end_date_str)
                if end_date < start_date:
                    return RC(E_RC.RC_INVALID_INPUT, 'Start date must earlier than end date')
                
                return start_date, end_date
            
            except ValueError:
                return RC(E_RC.RC_INVALID_INPUT, 'Invalid date format')
        else:
            return RC(E_RC.RC_INVALID_INPUT, 'Invalid date range type')
        
    def _calculate_salary(self, total_hours_worked: float|str, salary: float|str) ->float:
        """
        Calculates the salary for a user based on their total hours worked and hourly salary.

        This method takes the total hours worked (which can be provided as a float or a string) and the 
        hourly salary (also as a float or string) and calculates the total salary payment. It converts 
        the total hours worked from seconds to hours before performing the calculation.

        Args:
            total_hours_worked (float|str): The total number of hours worked, in seconds.
            salary (float|str): The hourly salary.

        Returns:
            float: The calculated salary payment.
        """
        return (float(total_hours_worked) / 3600.0) * float(salary)
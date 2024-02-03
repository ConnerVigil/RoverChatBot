from datetime import datetime
import json
from db_services import *
from email_services import send_lead_to_sales_team
import pytz


def get_current_date_and_time(company_time_zone: str) -> str:
    """
    Gets the current date and time

    Args:
        company_time_zone (str): The time zone of the company

    Returns:
        str: The current date and time
    """
    utc_now = datetime.datetime.utcnow()
    company_timezone = pytz.timezone(company_time_zone)
    current_date_time = utc_now.replace(tzinfo=pytz.utc).astimezone(company_timezone)
    return current_date_time.isoformat()


def save_customers_personal_information(
    phone_number: str, first_name: str = None, last_name: str = None, email: str = None
):
    """Saves the customer's personal information to the database

    Args:
        phone_number (str): The phone number of the customer
        first_name (str, optional): The first name of the customer. Defaults to None.
        last_name (str, optional): The last name of the customer. Defaults to None.
        email (str, optional): The email of the customer. Defaults to None.

    Returns:
        str: A string confirming that the information was saved
    """
    res = update_user(phone_number, first_name, last_name, email)
    return json.dumps({"result": "Customer information saved"})


def pass_customer_to_representative(
    first_name: str, last_name: str, email: str, callback_times: list
) -> str:
    print("Passing customer to representative...")
    print(f"First Name: {first_name}")
    print(f"Last Name: {last_name}")
    print(f"Email: {email}")
    print(f"Callback Times: {callback_times}")
    # send_lead_to_sales_team()
    return json.dumps({"result": "Customer passed to representative"})


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date_and_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_time_zone": {
                        "type": "string",
                        "description": "The time zone of the company. For example, 'US/Pacific' or 'US/Eastern'",
                    },
                },
                "required": ["company_time_zone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_customers_personal_information",
            "description": "Save the customer's personal information to the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "description": "The customer's first name",
                    },
                    "last_name": {
                        "type": "string",
                        "description": "The customer's last name",
                    },
                    "email": {
                        "type": "string",
                        "description": "The customer's email",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pass_customer_to_representative",
            "description": "Pass the customer to a representative by email",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "description": "The customer's first name",
                    },
                    "last_name": {
                        "type": "string",
                        "description": "The customer's last name",
                    },
                    "email": {
                        "type": "string",
                        "description": "The customer's email",
                    },
                    "callback_times": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of times the representative can call the customer",
                    },
                },
                "required": ["first_name", "last_name", "email", "callback_times"],
            },
        },
    },
]

available_functions = {
    "get_current_date_and_time": {
        "function": get_current_date_and_time,
        "parameters": [],
    },
    "save_customers_personal_information": {
        "function": save_customers_personal_information,
        "parameters": ["first_name", "last_name", "email"],
    },
    "pass_customer_to_representative": {
        "function": pass_customer_to_representative,
        "parameters": ["first_name", "last_name", "email", "callback_times"],
    },
}

from datetime import datetime
import json
from db_services import *


def book_appointment(date: str, time: str) -> str:
    """
    Books an appointment for an inspection

    Args:
        date (str): The date of the appointment
        time (str): The time of the appointment

    Returns:
        str: A string confirming the appointment
    """
    print("Booking Appointment...")
    return json.dumps({"date booked": date, "time booked": time})


def get_current_date_and_time() -> str:
    """
    Gets the current date and time

    Returns:
        str: The current date and time
    """
    current_date_time = datetime.now()
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
    return json.dumps({"information saved": True})


def pass_customer_to_representative(user: object) -> str:
    """Passes the customer to a representative

    Args:
        user (object): The user object

    Returns:
        str: A string confirming that the customer was passed to a representative
    """
    res = insert_user(user)
    return json.dumps({"customer passed to representative": True}


tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date of the appointment",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of the appointment",
                    },
                },
                "required": ["date", "time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date_and_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
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
]

available_functions = {
    "book_appointment": {
        "function": book_appointment,
        "parameters": ["date", "time"],
    },
    "get_current_date_and_time": {
        "function": get_current_date_and_time,
        "parameters": [],
    },
    "save_customers_personal_information": {
        "function": save_customers_personal_information,
        "parameters": ["first_name", "last_name", "email"],
    },
}

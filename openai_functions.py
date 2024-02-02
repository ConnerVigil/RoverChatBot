from datetime import datetime
import json
from db_services import *
from email_services import send_lead_to_sales_team


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



tools = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "book_appointment",
    #         "description": "Book an appointment for the customer",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "date": {
    #                     "type": "string",
    #                     "description": "The date of the appointment",
    #                 },
    #                 "time": {
    #                     "type": "string",
    #                     "description": "The time of the appointment",
    #                 },
    #             },
    #             "required": ["date", "time"],
    #         },
    #     },
    # },
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
    # "book_appointment": {
    #     "function": book_appointment,
    #     "parameters": ["date", "time"],
    # },
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

import os
from dotenv import load_dotenv
from datetime import datetime
import json
from db_services import *
from email_services import send_email
import pytz

load_dotenv()


def get_current_date_and_time(company_time_zone: str) -> str:
    """
    Gets the current date and time

    Args:
        company_time_zone (str): The time zone of the company

    Returns:
        str: The current date and time
    """
    utc_now = datetime.utcnow()
    company_timezone = pytz.timezone(company_time_zone)
    current_date_time = utc_now.replace(tzinfo=pytz.utc).astimezone(company_timezone)
    return current_date_time.isoformat()


def save_customers_personal_information(
    phone_number: str, first_name: str, last_name: str, email: str
):
    """
    Saves the customer's personal information to the database

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
    first_name: str,
    last_name: str,
    email: str,
    callback_times: str,
    customer_status: str,
    summary_of_interation: str,
    company_time_zone: str,
) -> str:
    """
    Passes the customer to a representative by email

    Args:
        first_name (str): The customer's first name
        last_name (str): The customer's last name
        email (str): The customer's email
        callback_times (str): Times the representative can call the customer
        summary_of_interation (str): A summary of the interaction with the customer

    Returns:
        str: A string confirming that the customer was passed to the representative
    """
    formatted_time = "No phone number information"
    missed_call_time = "No missed call information"
    phone_number = "No phone number information"
    company_name = "No company information"
    user_result = get_user_by_email(email)

    company_result = get_company_by_id(user_result.data[0]["company_id"])
    company = company_result.data[0]
    company_name = company["name"]
    recording_sid = None

    phone_number = user_result.data[0]["phone_number"]
    missed_call_result = get_missed_call_by_phone_number(phone_number)
    if len(missed_call_result.data) == 1:
        missed_call_time = missed_call_result.data[0]["created_at"]

        date_time_object = datetime.fromisoformat(missed_call_time)
        company_time_zone_obj = pytz.timezone(company_time_zone)
        date_time_in_tz = date_time_object.replace(tzinfo=pytz.utc).astimezone(
            company_time_zone_obj
        )
        formatted_time = date_time_in_tz.strftime("%m/%d/%Y %I:%M %p")
        recording_sid = missed_call_result.data[0]["recording_sid"]

    body = f"""
    <html>
        <body>
            <p><strong>Company Name:</strong> {company_name}</p>
            <p><strong>Customer Name:</strong> {first_name} {last_name}</p>
            <p><strong>Phone Number:</strong> {phone_number}</p>
            <p><strong>Missed Call Time:</strong> {formatted_time} {company_time_zone}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Customer status:</strong> {customer_status}</p>
            <p><strong>Callback Times:</strong> {callback_times}</p>
            <p><strong>Summary of Interaction:</strong> {summary_of_interation}</p>
        </body>
    </html>
    """

    recipients = ["talmage@textrover.co", "conner@textrover.co"]
    addresses = []

    if os.getenv("SENTRY_ENVIRONMENT") == "production":
        if customer_status == "new":
            addresses = company["email_addresses_new"]
        else:
            addresses = company["email_addresses_existing"]

    recipients.extend(addresses)

    send_email(
        subject="New Lead From Rover AI",
        body=body,
        sender="conner@textrover.co",
        recipients=recipients,
        attachment_bucket="voicemail-recordings",
        attachment_file_name=recording_sid,
        is_html=True,
    )

    return json.dumps({"result": "Customer passed to representative"})


tools = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_current_date_and_time",
    #         "description": "Get the current date and time",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "company_time_zone": {
    #                     "type": "string",
    #                     "description": "The time zone of the company. For example, 'US/Pacific' or 'US/Eastern'",
    #                 },
    #             },
    #             "required": ["company_time_zone"],
    #         },
    #     },
    # },
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
                "required": ["first_name", "last_name", "email"],
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
                        "type": "string",
                        "description": "A list of times the representative can call the customer",
                    },
                    "customer_status": {
                        "type": "string",
                        "description": "The status of the customer, either 'new' or 'existing'",
                    },
                    "summary_of_interation": {
                        "type": "string",
                        "description": "A summary of the interaction with the customer",
                    },
                    "company_time_zone": {
                        "type": "string",
                        "description": "The time zone of the company. For example, 'US/Pacific' or 'US/Eastern'",
                    },
                },
                "required": [
                    "first_name",
                    "last_name",
                    "email",
                    "callback_times",
                    "customer_status",
                    "summary_of_interation",
                    "company_time_zone",
                ],
            },
        },
    },
]

available_functions = {
    # "get_current_date_and_time": {
    #     "function": get_current_date_and_time,
    #     "parameters": ["company_time_zone"],
    # },
    "save_customers_personal_information": {
        "function": save_customers_personal_information,
        "parameters": ["first_name", "last_name", "email"],
    },
    "pass_customer_to_representative": {
        "function": pass_customer_to_representative,
        "parameters": [
            "first_name",
            "last_name",
            "email",
            "callback_times",
            "customer_status",
            "summary_of_interation",
            "company_time_zone",
        ],
    },
}

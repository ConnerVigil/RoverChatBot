import datetime
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

print(get_current_date_and_time("US/Pacific"))

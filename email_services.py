import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()


def send_lead_to_sales_team(body: str, recipients: list[str]):
    """
    Sends a lead to the sales team

    Args:
        body (str): The body of the email
        recipients (list[str]): A list of email addresses to send the lead to
    """
    subject = "New Lead from Rover AI"
    sender = "conner@textrover.co"
    send_email(subject=subject, body=body, sender=sender, recipients=recipients)


def send_email(subject: str, body: str, sender: str, recipients: list[str]):
    """
    Sends an email

    Args:
        subject (str): The subject of the email
        body (str): The body of the email
        sender (str): The email address of the sender
        recipients (list[str]): A list of email addresses to send the email to
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())


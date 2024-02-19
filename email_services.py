import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


def send_lead_to_sales_team(body: str, recipients: list[str]):
    """
    Sends a lead to the sales team from conner's work email

    Args:
        body (str): The body of the email
        recipients (list[str]): A list of email addresses to send the lead to
    """
    subject = "New Lead from Rover AI"
    sender = "conner@textrover.co"
    send_email(
        subject=subject, body=body, sender=sender, recipients=recipients, is_html=True
    )


def send_email(
    subject: str, body: str, sender: str, recipients: list[str], is_html: bool = False
):
    """
    Sends an email

    Args:
        subject (str): The subject of the email
        body (str): The body of the email
        sender (str): The email address of the sender
        recipients (list[str]): A list of email addresses to send the email to
        is_html (bool): If True, the body is treated as HTML. Default is False.
    """
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    if is_html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.quit()

from email.mime.application import MIMEApplication
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from db_services import download_file_from_supabase

load_dotenv()


def send_email(
    subject: str,
    body: str,
    sender: str,
    recipients: list[str],
    attachment_bucket: str = None,
    attachment_file_name: str = None,
    is_html: bool = False,
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

    if attachment_file_name:
        attachment_data = download_file_from_supabase(
            attachment_bucket, attachment_file_name
        )

        attachment = MIMEApplication(attachment_data)
        attachment.add_header(
            "Content-Disposition", "attachment", filename=attachment_file_name + ".wav"
        )

        msg.attach(attachment)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.quit()

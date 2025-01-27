import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

#create a function to send email
def send_email(smtp_server = "smtp.gmail.com", port = 465, sender_email = "ia2epd@gmail.com",
                receiver_email = "ia2epd@gmail.com", password = os.getenv('EMAIL_PASS'), message_text = "") -> None:
    '''
    Send an email containing the provided message text to a specified email address.

    Args:
        message_text (str): The body text of the email message.

    Raises:
        This function may raise exceptions if there are issues sending the email, such as authentication errors or network problems.

    Returns:
        None
    '''
    message = MIMEMultipart("alternative")
    message["Subject"] = "Platform Status"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text
    text = message_text

    # Turn these into plain MIMEText objects
    part1 = MIMEText(text, "plain")

    # Add HTML/plain-text parts to MIMEMultipart message

    message.attach(part1)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
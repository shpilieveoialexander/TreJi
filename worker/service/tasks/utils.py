import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..core.settings import settings


def get_default_now() -> str:
    """Return UTC+3"""
    return datetime.utcnow()


def send_email(recipient_email: str, subject: str, body: str):
    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach the body as HTML
        msg.attach(MIMEText(body, "html"))

        # Connect to the SMTP server
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            server.sendmail(settings.SMTP_USER, recipient_email, msg.as_string())

    except Exception as e:
        return f"Failed to send email: {str(e)}"
    return f"Email sent to {recipient_email}"

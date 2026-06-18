from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.config.settings import settings
from app.utils.logger import logger

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
env = Environment(
    loader=FileSystemLoader(BASE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


async def send_email(to_email: str, subject: str, html_content: str):
    # Container message
    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.mail_from_name} <{settings.mail_from_email}>"
    message["To"] = to_email
    message["Subject"] = subject

    # HTML part
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    # Send email via Mailtrap SMTP
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.mailtrap_host,
            port=settings.mailtrap_port,
            username=settings.mailtrap_user,
            password=settings.mailtrap_password,
            start_tls=settings.mailtrap_secure,
        )
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")


def render_verification_email(name: str, token: str) -> str:
    template = env.get_template("verify_email.html")
    verify_url = f"{settings.frontend_url}/auth/verify-email/{token}"
    return template.render(name=name, verify_url=verify_url)


def render_password_reset_email(name: str, token: str) -> str:
    template = env.get_template("reset_password.html")
    reset_url = f"{settings.frontend_url}/auth/reset-password/{token}"
    return template.render(name=name, reset_url=reset_url)


def render_account_creation_email(name: str, email: str, password: str) -> str:
    template = env.get_template("account_creation.html")
    login_url = f"{settings.frontend_url}/auth/login"
    return template.render(name=name, email=email, password=password, login_url=login_url)


async def send_account_creation_email(name: str, email: str, password: str) -> None:
    subject = "Your Account Has Been Created"
    html_content = render_account_creation_email(name, email, password)
    await send_email(email, subject, html_content)


def render_account_status_email(name: str, status: str) -> str:
    template = env.get_template("account_status.html")
    login_url = f"{settings.frontend_url}/auth/login"
    return template.render(name=name, status=status, login_url=login_url)


async def send_account_status_email(name: str, email: str, status: str) -> None:
    subject = f"Account Registration {status.capitalize()}"
    html_content = render_account_status_email(name, status)
    await send_email(email, subject, html_content)



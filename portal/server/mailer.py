import smtplib
from email.message import EmailMessage

from . import config


def send_code(to, name, code, minutes, link):
    _send(to, f"Your {config.SERVICE_NAME} verification code",
          f"Hello {name},\n\n"
          f"An administrator has added you as an officer on {config.SERVICE_NAME}.\n\n"
          f"Your verification code is: {code}\n\n"
          f"It works for {minutes} minutes. Enter it here and choose your password:\n{link}\n\n"
          "If you were not expecting this, you can ignore this email and no account will be created.\n")


def send_reset_code(to, name, code, minutes, link):
    _send(to, f"Reset your {config.SERVICE_NAME} password",
          f"Hello {name},\n\n"
          f"Someone asked to reset the password for your {config.SERVICE_NAME} officer account.\n\n"
          f"Your reset code is: {code}\n\n"
          f"It works for {minutes} minutes. Enter it here and choose a new password:\n{link}\n\n"
          "If this was not you, ignore this email. Your password has not changed.\n")


def _send(to, subject, body):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.SMTP_FROM or config.SMTP_USER
    message["To"] = to
    message.set_content(body)
    if config.SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=10)
    else:
        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10)
    with server:
        if config.SMTP_PORT != 465:
            server.starttls()
        if config.SMTP_USER:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(message)

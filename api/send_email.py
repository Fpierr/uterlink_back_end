#!/usr/bin/python3
"""To send email"""

from email.mime.text import MIMEText
import os
import smtplib


def send_email(email, code):
    """Send verification email with the given code to the specified email address."""
    try:
        msg = MIMEText(f"{code}\n")
        msg['Subject'] = 'Message Center'
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
            server.sendmail(os.getenv('EMAIL_USER'), email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
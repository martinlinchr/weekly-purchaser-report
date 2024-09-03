import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email(recipient, subject, body, attachment_path):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, 'rb') as file:
        attachment = MIMEApplication(file.read(), _subtype="csv")
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg.attach(attachment)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print(f"Email sent to {recipient} with attachment {attachment_path}")

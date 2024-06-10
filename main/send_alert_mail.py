from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
import os
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()
# email_password = os.environ.get("MY_PASSWORD")
email_password = "iybw apas orcf mdmm"

def send_mail(email_receiver, body):
    email_sender = 'thedatadude000@gmail.com'
    receiver_name = 'UpTrackr'  

    # Generate a unique identifier for the email subject
    email_subject = f'New Upwork Gig Alert - [{str(uuid.uuid4())[:8]}]'

    msg = MIMEMultipart('alternative')
    msg['From'] = f'{receiver_name} <{email_sender}>'
    msg['To'] = email_receiver
    msg['Subject'] = email_subject

    html_body = MIMEText(body, 'html')

    msg.attach(html_body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, msg.as_string())
        
        




from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# email_password = os.environ.get("MY_PASSWORD")
email_password = "moca yzvv vyaw synx"




def send_reset_password_mail(email_receiver,username, activation_link):
    email_sender =  'alerts@uptrackr.co'
    email_password = "moca yzvv vyaw synx"

    email_receiver = f'{email_receiver}'
    receiver_name = 'UpTrackr'  
    subject = 'Password Reset'
    em = EmailMessage()
    em['From'] = f'{receiver_name} <{email_sender}>'  # Custom name and email
    em['To'] = email_receiver
    em['Subject'] = subject
    
    body = f"""
    Hi {username},

    You have requested to reset your password for account. Please click on the link below to reset your password:

    {activation_link}

    If you did not request this password reset, you can safely ignore this email. Your password will remain unchanged.
    Thanks,
    Uptrackr.
                                    
                   """
                   
    body = '\n'.join(line.strip() for line in body.split('\n'))
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
        



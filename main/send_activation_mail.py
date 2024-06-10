from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
email_password = os.environ.get("MY_PASSWORD")



def send_activation_mail(email_receiver, username, activation_link):
    email_sender =  'thedatadude000@gmail.com'
    email_password = os.environ.get("MY_PASSWORD")
    print('This is........')
    print(email_sender)
    print(email_password)

    email_receiver = f'{email_receiver}'
    receiver_name = 'UpTrackr'  
    subject = 'Activate your account'
    em = EmailMessage()
    em['From'] = f'{receiver_name} <{email_sender}>'  # Custom name and email
    em['To'] = email_receiver
    em['Subject'] = subject
    
    body = f"""
    Hi {username}, Welcome to Uptrackr!
                   
    Click the link below to activate your account and start using our services:
                   
    {activation_link}

    If you have any questions, just let us know.

    Thanks,
    Uptrackr.
                                    
                   """
                   
    body = '\n'.join(line.strip() for line in body.split('\n'))
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
        



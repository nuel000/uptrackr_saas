# MAIN CODE
import re
import html
import schedule
import time
import xml.etree.ElementTree as ET
import requests
import sys
# from send_alert_mail import send_mail 
import signal




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
        



def format_description(text):
  new = re.sub('<.*?>', '', text)
  pattern = r'Posted On: [^<]+'
  pattern2 = r'\s?(Hourly Range: \$\d+\.\d+-\$\d+\.\d+|Budget: \$\d+)\s*$'
  cleaned_text = re.sub(pattern, '', new)
  new_cleaned = re.sub(pattern2, '',  cleaned_text)
  cleaned_text = html.unescape(new_cleaned)

  return cleaned_text

# Set to store unique job IDs
processed_job_ids = []

def fetch_xml_data(rss):
    # URL of the RSS feed
    rss_url = f"{rss}"

    # Fetch the XML data from the RSS feed
    response = requests.get(rss_url)
    if response.status_code == 200:
        return response.text
    else:
        pass
        return None

def parse_xml(xml_data):
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Initialize a list to store job information
    jobs = []

    # Ensure only up to 5 jobs are stored
    while len(jobs) >= 5:
        # print('max jobs reached for the list')
        jobs.pop(-1) 
        # print('last job removed len of list is', len(jobs))
        

    # Iterate over each <item> element in the XML
    for item in root.findall('.//item'):
        job = {}

        # Extract job details
        job['title'] = item.find('title').text.strip()
        job['title'] = html.unescape(job['title'])
        job['link'] = item.find('link').text.strip()
        job['description'] = item.find('description').text.strip()
        job['job_id'] = item.find('guid').text.strip()  # Assuming the <guid> tag contains a unique job ID

        # Check if job ID has already been processed
        if job['job_id'] in processed_job_ids:
            continue

        # Ensure only up to 5 processed job IDs are stored
        while len(processed_job_ids) >= 5:
            # print('len of Job IDs has exceeded 5')
            processed_job_ids.pop(-1)
            # print('last job removed , len of list is ',len(processed_job_ids))

        # Extract additional job details
        additional_details = item.find('description').text.strip().split('<br />')
        for detail in additional_details:
            if 'Posted On' in detail:
                posted_on = detail.split(': ')
                if len(posted_on) > 1:
                    job['posted_on'] = posted_on[1]
            elif 'Category' in detail:
                category = detail.split(': ')
                if len(category) > 1:
                    job['category'] = category[1]
            elif 'Country' in detail:
                country = detail.split(': ')
                if len(country) > 1:
                    job['country'] = country[1]
            elif 'Budget' in detail:
                budget = detail.split(': ')
                if len(budget) > 1:
                    job['budget'] = budget[1]
            elif 'Hourly Range' in detail:
                rate = detail.split(': ')
                if len(rate) > 1:
                    job['rate'] = rate[1] +" hourly"
            else:
                job['non'] = 'Hourly, Not Specified'
                

        # Add job ID to the set of processed job IDs
        processed_job_ids.append(job['job_id'])

        # Add job to the list
        jobs.append(job)

    return jobs



prev_job = {}  # Initialize outside the function

def get_budget(job):
    if 'budget' in job:
        return job['budget']
    elif 'rate' in job:
        return job['rate']
    elif 'non' in job:
        return job['non']
    else:
        return "Not specified"

def job(email, rss_url):
    global processed_job_ids  # Access the global variable
    global prev_job

    xml_data = fetch_xml_data(rss_url)
    if xml_data:
        jobs = parse_xml(xml_data)
        new_job = jobs[0] 
        if new_job != prev_job:
            try:
                client_country = new_job['country']
            except KeyError:
                client_country = 'None Specified'  
                    
            body = f"""
            <html>
                <body>
                
                <b>Hi there, New Gig Available on Upwork, checkout details below 👇.</b>
                
                <br>
                <br>

                <b>Title</b>: {new_job['title']}<br>
                <br>
                <b>Description</b>: {format_description(new_job['description'])}<br>
                <br>
                <b>Posted On</b>: {new_job['posted_on']}<br>
                <br>
                <b>Category</b>: {new_job['category']}<br>
                <br>
                <b>Budget</b>: {get_budget(new_job)}<br>
                <br>
                <b>Client Country</b>: {client_country}<br>
                <br>
                <b>APPLY HERE</b>: <a href="{new_job['link']}">Link to Apply</a><br>
                <br>
                <br>
                <br>
                <b> Keep Winning!! 💪</b>
                <br>
                <br>
                Uptrackr Team.
                </body>
            </html>
            """     
            # Remove leading whitespace from each line
            body = '\n'.join(line.strip() for line in body.split('\n'))              
            send_mail(email,body)
            prev_job = new_job
        else:
            pass
    else:
        pass
 
 
    
def main(email, rss_url):
    running = True

    def signal_handler(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, signal_handler)

    # Schedule job to run every 10 minutes
    schedule.every(1).seconds.do(job, email, rss_url)

    while running:
        schedule.run_pending()
        time.sleep(1)  # Sleep to prevent high CPU usage
    print('script stopped')

if __name__ == '__main__':
    email = sys.argv[1]
    rss_url = sys.argv[2]
    main(email, rss_url)


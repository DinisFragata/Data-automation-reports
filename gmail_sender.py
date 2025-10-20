from gmail_auth import get_gmail_credentials
from googleapiclient.discovery import build
from email.message import EmailMessage
import base64
import os

def send_email_gmail(recipients, subject, body, attachment_path=None):
    creds = get_gmail_credentials()
    if creds is None:
        print("Email sending skipped by user.")
        return # User chose not to authorize email sending
    
    service = build('gmail', 'v1', credentials=creds)
    
    message = EmailMessage()
    message['To'] = ', '.join(recipients)
    message['From'] = 'me'
    message['Subject'] = subject
    message.set_content(body)
    
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        message.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
    
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    send_message = service.users().messages().send(userId='me', body=create_message).execute()
    print(f"Email sent!")
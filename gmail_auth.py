from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_credentials():
    creds = None
    if os.path.exists('token.pickle'): # Check if token.pickle file exists (the file for storing the email credentials)
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            print("You need to connect to your Google account to authorize access. (The emails will be sent from your account.)")
            choice = input("If you want to connect your email, press 'y'; to skip email sending, press 'n': ").strip().lower()
            if choice == 'n':
                print("Skipping email authorization.")
                return None
            creds = flow.run_local_server(port=0)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
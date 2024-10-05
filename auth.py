import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

def authenticate_google_calendar():
    try:
        print("Script started")
        creds = None

        print(f"Checking if {TOKEN_FILE} exists...")
        if os.path.exists(TOKEN_FILE):
            print(f"Loading credentials from {TOKEN_FILE}")
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing credentials...")
                creds.refresh(Request())
            else:
                print("Running OAuth flow with credentials.json...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, 'w') as token:
                print(f"Saving new credentials to {TOKEN_FILE}")
                token.write(creds.to_json())

        return creds

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    authenticate_google_calendar()

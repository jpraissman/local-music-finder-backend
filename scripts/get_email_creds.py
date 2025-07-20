import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
import dotenv
from scripts.models.email_creds import EmailCreds
from app import db

def get_email_creds():
  # Load environment variables
  dotenv_file = dotenv.find_dotenv()
  dotenv.load_dotenv(dotenv_file, override=True)

  # Grab the remaining creds from the database
  database_creds: EmailCreds = EmailCreds.query.first()

  try:
    # Create creds using the information in the environment variables
    creds = Credentials(
      token=database_creds.get_google_access_token(),
      refresh_token=os.environ.get('GOOGLE_REFRESH_TOKEN'),
      token_uri="https://oauth2.googleapis.com/token",
      client_id=os.environ.get('GOOGLE_TOKEN_CLIENT_ID'),
      client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
      scopes=["https://www.googleapis.com/auth/gmail.send"],
      universe_domain="googleapis.com",
      account="",
      expiry=datetime.strptime(database_creds.google_expiry, "%Y-%m-%dT%H:%M:%S.%fZ") 
    )
    
    # If there are creds are expired, refresh the token
    if not creds.valid:
      print("Creds not valid")
      if creds.expired and creds.refresh_token:
        print("Trying to refresh")
        creds.refresh(Request())

        # Save the new creds back to the database
        database_creds.set_google_access_token(creds.token)
        database_creds.google_expiry = creds.expiry.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        db.session.commit()
      
        print("Refresh successful")

    return creds
  except Exception as e:
    print(f"A creds error occured: {e}")
    return None

  
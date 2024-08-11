import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
import dotenv
import heroku3

def get_email_creds():
  # Load environment variables
  dotenv_file = dotenv.find_dotenv()
  dotenv.load_dotenv(dotenv_file, override=True)

  try:
    # Create creds using the information in the environment variables
    creds = Credentials(
      token=os.environ.get('GOOGLE_ACCESS_TOKEN'),
      refresh_token=os.environ.get('GOOGLE_REFRESH_TOKEN'),
      token_uri="https://oauth2.googleapis.com/token",
      client_id=os.environ.get('GOOGLE_TOKEN_CLIENT_ID'),
      client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
      scopes=["https://www.googleapis.com/auth/gmail.send"],
      universe_domain="googleapis.com",
      account="",
      expiry=datetime.strptime(os.environ.get('GOOGLE_EXPIRY'), "%Y-%m-%dT%H:%M:%S.%fZ") 
    )
    
    # If there are creds are expired, refresh the token
    if not creds.valid:
      print("Here")
      if creds.expired and creds.refresh_token:
        print("Trying to refresh")
        creds.refresh(Request())

        # Update environment variables differently depending on where this code is running
        if (os.environ.get("ENVIRONMENT") == "Localhost"):
          dotenv.set_key(dotenv_file, "GOOGLE_ACCESS_TOKEN", creds.token)
          dotenv.set_key(dotenv_file, "GOOGLE_EXPIRY", creds.expiry.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        elif (os.environ.get("ENVIRONMENT") == "Heroku"):
          client = heroku3.from_key(os.environ.get("HEROKU_API_KEY"))
          app = client.apps()["music-finder-backend"]
          app.update_config({
            'GOOGLE_ACCESS_TOKEN': creds.token,
            'GOOGLE_EXPIRY': creds.expiry.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
          })

    return creds
  except Exception as e:
    print(f"A creds error occured: {e}")
    return None

  
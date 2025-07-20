from app import db
from cryptography.fernet import Fernet
import os

FERNET_KEY = os.environ["FERNET_KEY"] 
fernet = Fernet(FERNET_KEY)

class EmailCreds(db.Model):
    __tablename__ = "email_creds"

    id: int = db.Column(db.Integer, primary_key=True)

    google_access_token = db.Column("google_access_token", db.String, nullable=False)
    google_expiry = db.Column("google_expiry", db.String, nullable=False)

    def __init__(self, google_access_token: str, google_expiry):
        self.google_access_token = fernet.encrypt(google_access_token.encode()).decode()
        self.google_expiry = google_expiry
    
    def get_google_access_token(self):
        return fernet.decrypt(self.google_access_token.encode()).decode()
    
    def set_google_access_token(self, token: str):
        self.google_access_token = fernet.encrypt(token.encode()).decode()
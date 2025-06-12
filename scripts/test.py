from scripts.models.session import Session
from app import db

sessions: list[Session] = Session.query.all()

for session in sessions:
  session.num_bands_viewed = 0
  session.num_venues_viewded = 0
db.session.commit()
  
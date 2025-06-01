from app import db
from datetime import datetime
import pytz

class Activity(db.Model):
  __tablename__ = "activity"

  id: int = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, nullable=False)
  session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
  session = db.relationship("Session", back_populates=False)
  page: str = db.Column(db.String, nullable=False)
  user_agent: str = db.Column(db.String)
  ip: str = db.Column(db.String)
  referer: str = db.Column(db.String)

  def __init__(self, session_id: int, page: str, user_agent: str, ip: str, referer: str):
    self.session_id = session_id
    self.page = page
    self.user_agent = user_agent
    self.ip = ip
    self.referer = referer
    self.created_at = datetime.now(pytz.timezone("US/Eastern"))

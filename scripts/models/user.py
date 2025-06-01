from app import db
from sqlalchemy.orm import Mapped
from scripts.models.session import Session
from datetime import datetime, timedelta
import pytz

class User(db.Model):
  __tablename__ = "user"

  id: str = db.Column(db.String, primary_key=True)
  sessions: Mapped[list[Session]] = db.relationship("Session", back_populates="user", cascade="all, delete-orphan")

  def __init__(self, id: str):
    self.id = id
    self.sessions = []

  # Converts a datetime to eastern time
  def to_eastern_time(self, dt):
    eastern = pytz.timezone("US/Eastern")
    if dt.tzinfo is None:
        return eastern.localize(dt)
    else:
        return dt.astimezone(eastern)

  # True if there is an active session for the user. False otherwise
  def has_active_session(self):
    if len(self.sessions) == 0:
      return False
    last_session = self.sessions[-1]
    last_session_end_time = self.to_eastern_time(last_session.end_time)
    cur_time = datetime.now(pytz.timezone("US/Eastern"))
    return (cur_time - last_session_end_time) < timedelta(minutes=90)
  
  # Returns the active session for the user. If there is no active session, it creates a new one.
  def get_active_session(self):
    if self.has_active_session():
      return self.sessions[-1]
    else:
      new_session = Session(self.id)
      db.session.add(new_session)
      self.sessions.append(new_session)
      return new_session

  def add_activity(self, page: str, user_agent: str, ip: str, referer: str):
    active_session = self.get_active_session()
    active_session.add_activity(page, user_agent, ip, referer)

  def add_event_view(self, event_id: int):
    active_session = self.get_active_session()
    active_session.add_event_view(event_id)
  
  def add_video_click(self, event_id: int):
    active_session = self.get_active_session()
    active_session.add_video_click(event_id)
  



  
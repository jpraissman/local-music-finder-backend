from app import db
from sqlalchemy.orm import Mapped
from scripts.models.session import Session
from datetime import timedelta
from scripts.date_helpers import get_eastern_datetime_now, convert_to_eastern, get_eastern_datetime_now_str

class User(db.Model):
  __tablename__ = "user"

  id: str = db.Column(db.String, primary_key=True)
  sessions: Mapped[list[Session]] = db.relationship("Session", back_populates="user", cascade="all, delete-orphan")
  created_at = db.Column(db.DateTime)
  user_agents = db.Column(db.ARRAY(db.String))
  ip_addresses = db.Column(db.ARRAY(db.String))
  referers = db.Column(db.ARRAY(db.String))

  def __init__(self, id: str):
    self.id = id
    self.sessions = []
    self.created_at = get_eastern_datetime_now_str()
    self.user_agents = []
    self.ip_addresses = []
    self.referers = []

  # True if there is an active session for the user. False otherwise
  def has_active_session(self):
    if len(self.sessions) == 0:
      return False
    last_session_end_time = convert_to_eastern(self.sessions[-1].end_time)
    cur_time = get_eastern_datetime_now()
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
    
    if user_agent not in self.user_agents:
      updated_user_agents = list(self.user_agents)
      updated_user_agents.append(user_agent)
      self.user_agents = updated_user_agents
    if ip not in self.ip_addresses:
      updated_ip_addresses = list(self.ip_addresses)
      updated_ip_addresses.append(ip)
      self.ip_addresses = updated_ip_addresses
    if referer not in self.referers:
      updated_referers = list(self.referers)
      updated_referers.append(referer)
      self.referers = updated_referers

  def add_event_view(self, event_id: int):
    active_session = self.get_active_session()
    active_session.add_event_view(event_id)
  
  def add_video_click(self, event_id: int):
    active_session = self.get_active_session()
    active_session.add_video_click(event_id)
  



  
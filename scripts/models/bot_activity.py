from app import db
from datetime import datetime
import pytz

class BotActivity(db.Model):
  __tablename__ = "bot_activity"

  id: int = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, nullable=False)
  page: str = db.Column(db.String, nullable=False)
  user_agent: str = db.Column(db.String)
  ip: str = db.Column(db.String)
  referer: str = db.Column(db.String)
  is_query: str = db.Column(db.Boolean)

  def __init__(self, page: str, user_agent: str, ip: str, referer: str, is_query: bool):
    self.page = page
    self.user_agent = user_agent
    self.ip = ip
    self.referer = referer
    self.created_at = datetime.now(pytz.timezone("US/Eastern"))
    self.is_query = is_query

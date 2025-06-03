from app import db
from scripts.date_helpers import get_eastern_datetime_now_str

# Represents an event that was viewed by a user
class EventView(db.Model):
  __tablename__ = "event_view"

  id: int = db.Column(db.Integer, primary_key=True)
  created_datetime = db.Column(db.DateTime, nullable=False)
  event_id = db.Column(db.Integer, db.ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
  event = db.relationship("Event", back_populates="event_views")
  session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
  session = db.relationship("Session", back_populates=False)

  def __init__(self, event_id: int, session_id: int):
    self.event_id = event_id
    self.session_id = session_id
    self.created_datetime = get_eastern_datetime_now_str()
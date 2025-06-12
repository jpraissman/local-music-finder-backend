from app import db
from sqlalchemy.orm import Mapped
from scripts.models.activity import Activity
from scripts.models.event_view import EventView
from scripts.models.video_click import VideoClick
from scripts.date_helpers import get_eastern_datetime_now_str

class Session(db.Model):
  __tablename__ = "session"

  id: int = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  end_time = db.Column(db.DateTime, nullable=False)
  user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
  user = db.relationship("User", back_populates=False)
  activities: Mapped[list[Activity]] = db.relationship("Activity", back_populates="session", cascade="all, delete-orphan")
  viewed_events: Mapped[list[EventView]] = db.relationship("EventView", back_populates="session", cascade="all, delete-orphan")
  clicked_videos: Mapped[list[VideoClick]] = db.relationship("VideoClick", back_populates="session", cascade="all, delete-orphan")
  num_venues_viewded = db.Column(db.Integer, default=0)
  num_bands_viewed = db.Column(db.Integer, default=0)
  user_agent = db.Column(db.String)
  referer = db.Column(db.String)

  def __init__(self, user_id: str):
    self.start_time = get_eastern_datetime_now_str()
    self.end_time = get_eastern_datetime_now_str()
    self.user_id = user_id
    self.activities = []
    self.viewed_events = []
    self.user_agent = "Unknown"
    self.referer = "Unknown"

  def add_activity(self, page: str, user_agent: str, ip: str, referer: str):
    new_activity = Activity(self.id, page, user_agent, ip, referer)
    db.session.add(new_activity)
    self.activities.append(new_activity)
    self.end_time = get_eastern_datetime_now_str()

    if self.user_agent == "Unknown":
      self.user_agent = user_agent
    if referer != None and self.referer == "Unknown" and "thelocalmusicfinder" not in referer:
      self.referer = referer

    if "/venue/" in page:
      self.add_venue_viewed()
    elif "/band/" in page:
      self.add_band_viewed()

  def add_event_view(self, event_id: int):
    new_event_view = EventView(event_id, self.id)
    db.session.add(new_event_view)
    self.viewed_events.append(new_event_view)

  def add_video_click(self, event_id: int):
    new_video_click = VideoClick(event_id, self.id)
    db.session.add(new_video_click)
    self.clicked_videos.append(new_video_click)
    self.end_time = get_eastern_datetime_now_str()

  def add_venue_viewed(self):
    if self.num_venues_viewded is None:
      self.num_venues_viewded = 1
    else:
      self.num_venues_viewded += 1
  
  def add_band_viewed(self):
    if self.num_bands_viewed is None:
      self.num_bands_viewed = 1
    else:
      self.num_bands_viewed += 1

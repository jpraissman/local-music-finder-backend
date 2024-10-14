from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List

class Query(db.Model):
  __tablename__ = "query"
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  time_range = db.Column(db.String, nullable=False)
  location = db.Column(db.String, nullable=False)
  distance = db.Column(db.String, nullable=False)
  genres = db.Column(ARRAY(db.String), nullable=False)
  band_types = db.Column(ARRAY(db.String), nullable=False)

  def __init__(self, time_range: str, location: str, distnce: str, genres: List[str], band_types: List[str]):
    self.time_range = time_range
    self.location = location
    self.distance = distnce
    self.genres = genres
    self.band_types = band_types
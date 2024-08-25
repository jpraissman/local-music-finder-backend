from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class User(db.Model):
  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  email_address = db.Column(db.String, nullable=False)
  address_description = db.Column(db.String, nullable=False)
  address_id = db.Column(db.String, nullable=False)
  max_distance = db.Column(db.String, nullable=False)
  max_distance_value = db.Column(db.Integer, nullable=False)
  genres = db.Column(ARRAY(db.String), nullable=False)
  band_types = db.Column(ARRAY(db.String), nullable=False)
  subscribed = db.Column(db.Boolean, nullable=False, default=True)

  def __init__(self, email_address, address_id, max_distance, genres, band_types,
               address_description, max_distance_value):
    self.email_address = email_address
    self.address_id = address_id
    self.max_distance = max_distance
    self.genres = genres
    self.band_types = band_types
    self.address_description = address_description
    self.max_distance_value = max_distance_value
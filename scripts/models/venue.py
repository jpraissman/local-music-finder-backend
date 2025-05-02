from app import db

class Venue(db.Model):
  __tablename__ = "venue"

  id: int = db.Column(db.Integer, primary_key=True)
  events = db.relationship("Event", back_populates="venue", cascade="all, delete-orphan")

  # Represent the most recent values
  venue_name: str = db.Column(db.String(50), nullable=False)
  address: str = db.Column(db.String, nullable=False)
  lat: float = db.Column(db.Float, nullable=False)
  lng: float = db.Column(db.Float, nullable=False)
  county: str = db.Column(db.String, nullable=True)

  def __init__(self, venue_name: str, address: str, lat: float, lng: float, county: str):
    self.venue_name = venue_name
    self.address = address
    self.lat = lat
    self.lng = lng
    self.county = county
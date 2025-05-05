from app import db

class Band(db.Model):
  __tablename__ = "band"

  id: int = db.Column(db.Integer, primary_key=True)
  events = db.relationship("Event", back_populates="band", cascade="all, delete-orphan")
  band_name: str = db.Column(db.String(50), nullable=False)

  # These represent the most recent values for this band (for auto-populating purposes)
  band_type: str = db.Column(db.String, nullable=False)
  tribute_band_name: str = db.Column(db.String, nullable=False)
  genres: list[str] = db.Column(db.ARRAY(db.String), nullable=False)

  def __init__(self, band_name: str, band_type: str, tribute_band_name: str, genres: list[str]):
    self.band_name = band_name
    self.band_type = band_type
    self.tribute_band_name = tribute_band_name
    self.genres = genres
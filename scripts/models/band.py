from app import db
from urllib.parse import urlparse, parse_qs

class Band(db.Model):
  __tablename__ = "band"

  id: int = db.Column(db.Integer, primary_key=True)
  events = db.relationship("Event", back_populates="band", cascade="all, delete-orphan")
  band_name: str = db.Column(db.String(50), nullable=False)
  youtube_ids: list[str] = db.Column(db.ARRAY(db.String), nullable=False)

  # These represent the most recent values for this band (for auto-populating purposes)
  band_type: str = db.Column(db.String, nullable=False)
  tribute_band_name: str = db.Column(db.String, nullable=False)
  genres: list[str] = db.Column(db.ARRAY(db.String), nullable=False)
  facebook_url: str = db.Column(db.String)
  instagram_url: str = db.Column(db.String)
  website_url: str = db.Column(db.String)

  def __init__(self, band_name: str, band_type: str, tribute_band_name: str, genres: list[str],
               facebook_url: str, instagram_url: str, website_url: str):
    self.band_name = band_name
    self.band_type = band_type
    self.tribute_band_name = tribute_band_name
    self.genres = genres
    self.youtube_ids = []
    self.facebook_url = facebook_url
    self.instagram_url = instagram_url
    self.website_url = website_url

  def extract_youtube_video_id(self, youtube_url: str) -> str | None:
    parsed_url = urlparse(youtube_url)
    
    if 'youtube.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    
    elif 'youtu.be' in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    
    return None

  def add_youtube_id(self, youtube_url):
    video_id = self.extract_youtube_video_id(youtube_url)
    if video_id is None or video_id in self.youtube_ids:
      return False
    else:
      self.youtube_ids.append(video_id)
      return True

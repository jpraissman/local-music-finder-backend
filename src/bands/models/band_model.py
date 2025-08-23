from app import db
from urllib.parse import urlparse, parse_qs
from src.bands.dto.band_dto import BandDTO
from src.bands.types.band_types import BandType
from src.bands.types.genres import Genre


class Band(db.Model):
    __tablename__ = "band"

    id: int = db.Column(db.Integer, primary_key=True)
    events = db.relationship(
        "Event", back_populates="band", cascade="all, delete-orphan"
    )
    band_name: str = db.Column(db.String(50), nullable=False)
    youtube_ids: list[str] = db.Column(db.ARRAY(db.String), nullable=False)
    band_type: BandType = db.Column(db.String, nullable=False)
    tribute_band_name: str = db.Column(db.String, nullable=False)
    genres: list[Genre] = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_url: str = db.Column(db.String, nullable=True)
    instagram_url: str = db.Column(db.String, nullable=True)
    website_url: str = db.Column(db.String, nullable=True)

    def __init__(self, band: BandDTO):
        self.band_name = band.band_name
        self.band_type = band.band_type
        self.tribute_band_name = band.tribute_band_name
        self.genres = band.genres
        self.youtube_ids = []
        self.facebook_url = band.facebook_url
        self.instagram_url = band.instagram_url
        self.website_url = band.website_url

    def extract_youtube_video_id(self, youtube_url: str) -> str | None:
        parsed_url = urlparse(youtube_url)

        if "youtube.com" in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            return query_params.get("v", [None])[0]

        elif "youtu.be" in parsed_url.netloc:
            return parsed_url.path.lstrip("/")

        return None

    def add_youtube_id(self, youtube_url):
        video_id = self.extract_youtube_video_id(youtube_url)
        if video_id is None or video_id in self.youtube_ids:
            return False
        else:
            self.youtube_ids.append(video_id)
            return True

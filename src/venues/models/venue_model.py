from app import db

from src.venues.dto.venue_dto import VenueDTO


class Venue(db.Model):
    __tablename__ = "venue"

    id: int = db.Column(db.Integer, primary_key=True)
    events = db.relationship(
        "Event", back_populates="venue", cascade="all, delete-orphan"
    )
    venue_name: str = db.Column(db.String, nullable=False)
    address: str = db.Column(db.String, nullable=False)
    lat: float = db.Column(db.Float, nullable=False)
    lng: float = db.Column(db.Float, nullable=False)
    county: str = db.Column(db.String, nullable=False)
    place_id: str = db.Column(db.String, nullable=False)
    town: str = db.Column(db.String, nullable=False)
    phone_number: str = db.Column(db.String, nullable=True)
    facebook_url: str = db.Column(db.String, nullable=True)
    instagram_url: str = db.Column(db.String, nullable=True)
    website_url: str = db.Column(db.String, nullable=True)

    def __init__(self, venue: VenueDTO):
        self.venue_name = venue.venue_name
        self.place_id = venue.venue_place_id
        self.phone_number = venue.phone_number
        self.facebook_url = venue.facebook_url
        self.instagram_url = venue.instagram_url
        self.website_url = venue.website
        self.lat = venue.lat
        self.lng = venue.lng
        self.county = venue.county
        self.town = venue.town
        self.address = venue.address

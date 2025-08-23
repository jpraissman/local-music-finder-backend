from app import db
from datetime import datetime
import pytz
from scripts.get_date_formatted import get_date_formatted
import random
from sqlalchemy.orm import Mapped
from scripts.models.event_view import EventView
from scripts.models.video_click import VideoClick
from src.events.dto.event_dto import EventDTO


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.Date, nullable=False)
    created_time = db.Column(db.Time, nullable=False)
    email_address = db.Column(db.String, nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    cover_charge = db.Column(db.Float, nullable=False)
    other_info = db.Column(db.String, nullable=True)
    band_or_venue = db.Column(db.String, nullable=True)
    event_id = db.Column(db.String, unique=True, nullable=False)
    email_sent = db.Column(db.Boolean, nullable=False, default=False)
    agrees_to_terms_and_privacy = db.Column(db.Boolean, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    venue = db.relationship("Venue", back_populates=False)
    band_id = db.Column(db.Integer, db.ForeignKey("band.id"), nullable=False)
    band = db.relationship("Band", back_populates=False)
    event_views: Mapped[list[EventView]] = db.relationship(
        "EventView",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    video_clicks: Mapped[list[VideoClick]] = db.relationship(
        "VideoClick",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __init__(self, event: EventDTO):
        self.event_date = event.event_date
        self.start_time = event.start_time
        self.end_time = event.end_time
        self.cover_charge = event.cover_charge
        self.other_info = event.other_info
        self.band_or_venue = event.band_or_venue
        self.event_id = event.event_id
        self.email_address = event.email_address
        self.created_date = (
            datetime.now(pytz.timezone("US/Eastern")).date().strftime("%Y-%m-%d")
        )
        self.created_time = (
            datetime.now(pytz.timezone("US/Eastern")).time().strftime("%H:%M:%S")
        )
        self.agrees_to_terms_and_privacy = True
        self.venue_id = event.venue_id
        self.band_id = event.band_id

    def set_distance_data(self, distance_formatted, distance_value):
        self.distance_formatted = distance_formatted
        self.distance_value = distance_value

    def get_all_details(self, include_event_id, include_email_address):
        # Create event_datetime_str
        event_date_str = self.event_date.strftime("%Y-%m-%d")
        event_time_str = self.start_time.strftime("%H:%M:%S")
        event_datetime_str = datetime.strptime(
            f"{event_date_str} {event_time_str}", "%Y-%m-%d %H:%M:%S"
        ).isoformat()
        # Create created_datetime_str and created_datetime_formatted
        created_date_str = self.created_date.strftime("%Y-%m-%d")
        created_time_str = self.created_time.strftime("%H:%M:%S")
        created_datetime_str = datetime.strptime(
            f"{created_date_str} {created_time_str}", "%Y-%m-%d %H:%M:%S"
        ).isoformat()
        created_datetime_formatted = datetime.strptime(
            f"{created_date_str} {created_time_str}", "%Y-%m-%d %H:%M:%S"
        ).strftime("%B %d, %Y at %#I:%M %p")

        return {
            "id": self.id,
            "venue_name": self.venue.venue_name,
            "band_name": self.band.band_name,
            "band_type": self.band.band_type,
            "start_time_formatted": self.start_time.strftime("%#I:%M %p"),
            "end_time": (
                None if self.end_time is None else self.end_time.strftime("%#I:%M %p")
            ),
            "cover_charge": self.cover_charge,
            "date_formatted": get_date_formatted(self.event_date),
            "distance_formatted": (
                self.distance_formatted if hasattr(self, "distance_formatted") else ""
            ),
            "address": self.venue.address,
            "genres": self.band.genres,
            "tribute_band_name": self.band.tribute_band_name,
            "other_info": self.other_info,
            "distance_value": (
                self.distance_value if hasattr(self, "distance_value") else -1
            ),
            "date_string": self.event_date.strftime("%Y-%m-%d"),
            "start_time_value": self.start_time.hour * 3600
            + self.start_time.minute * 60,
            "facebook_handle": self.facebook_handle,
            "instagram_handle": self.instagram_handle,
            "website": self.website,
            "phone_number": self.phone_number,
            "band_or_venue": self.band_or_venue,
            "email_address": (
                self.email_address if include_email_address else "Restricted"
            ),
            "created_date_formatted": created_datetime_formatted,
            "created_datetime": created_datetime_str,
            "event_datetime": event_datetime_str,
            "event_id": self.event_id if include_event_id else "Restricted",
            "county": self.venue.county,
            "place_id": self.venue.place_id,
            "youtube_id": (
                "" if len(self.band.youtube_ids) == 0 else self.band.youtube_ids[0]
            ),
            "ranking_position": random.randint(1, 100),
            "town": self.venue.town,
            "venue_id": self.venue_id,
            "band_id": self.band_id,
        }

    def get_metadata(self):
        return {
            "id": self.id,
            "created_date": self.created_date.strftime("%Y-%m-%d"),
            "created_time": self.created_time.strftime("%H:%M:%S"),
            "event_id": self.event_id,
        }

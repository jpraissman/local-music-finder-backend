from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time
from src.events.types.band_or_venue import BandOrVenue
from src.events.models.event_model import Event as EventModel


class EventDTO(BaseModel):
    id: int
    event_id: str = Field(..., max_length=8)
    band_name: str = Field(..., max_length=50)
    email_address: str = Field(..., max_length=100)
    event_date: date
    start_time: time
    end_time: Optional[time] = None
    cover_charge: float
    other_info: Optional[str] = Field(None, max_length=500)
    band_or_venue: BandOrVenue
    venue_id: int
    band_id: int


# TODO: Throw exception here?
def transform_from_event_model(event_model: EventModel) -> EventDTO:
    event_dto = EventDTO(**event_model)
    return event_dto

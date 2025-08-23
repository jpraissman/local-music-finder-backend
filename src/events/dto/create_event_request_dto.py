from pydantic import BaseModel, Field, EmailStr, HttpUrl, model_validator
from datetime import date, time
from typing import List, Optional
from src.bands.types.band_types import BandType
from src.bands.types.genres import Genre
from src.events.types.band_or_venue import BandOrVenue


class CreateEventRequestDTO(BaseModel):
    venue_name: str = Field(..., max_length=50)
    venue_place_id: str = Field(..., max_length=500)
    band_name: str = Field(..., max_length=50)
    band_type: BandType
    tribute_band_name: Optional[str] = Field("", max_length=100)
    genres: List[Genre]
    event_date: date
    start_time: time
    end_time: Optional[time] = None
    cover_charge: float = 0
    other_info: Optional[str] = Field("", max_length=500)
    website_url: Optional[HttpUrl] = Field(None, max_length=200)
    facebook_url: Optional[HttpUrl] = Field(None, max_length=200)
    instagram_url: Optional[HttpUrl] = Field(None, max_length=200)
    band_or_venue: BandOrVenue
    email_address: EmailStr = Field(..., max_length=100)

    @model_validator(mode="after")
    def check_tribute_band_name(self):
        if self.band_type == BandType.TRIBUTE_BAND and len(self.tribute_band_name) == 0:
            raise ValueError("Tribute band name must be provided for tribute bands.")
        return self

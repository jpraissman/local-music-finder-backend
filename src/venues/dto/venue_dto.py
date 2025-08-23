from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from src.venues.models.venue_model import Venue as VenueModel


class VenueDTO(BaseModel):
    venue_name: str = Field(..., max_length=50)
    venue_place_id: str = Field(..., max_length=500)
    website_url: Optional[HttpUrl] = Field(None, max_length=200)
    facebook_url: Optional[HttpUrl] = Field(None, max_length=200)
    instagram_url: Optional[HttpUrl] = Field(None, max_length=200)
    phone_number: Optional[str] = Field(None, max_length=20)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str
    county: str
    town: str
    id: int


# TODO: Throw exception here?
def transform_from_venue_model(venue_model: VenueModel) -> VenueDTO:
    venue_dto = VenueDTO(**venue_model, venue_place_id=venue_model.place_id)
    return venue_dto

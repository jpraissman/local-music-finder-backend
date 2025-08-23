from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class UpsertVenueRequestDTO(BaseModel):
    venue_name: str = Field(..., max_length=50)
    venue_place_id: str = Field(..., max_length=500)
    website_url: Optional[HttpUrl] = Field(None, max_length=200)
    facebook_url: Optional[HttpUrl] = Field(None, max_length=200)
    instagram_url: Optional[HttpUrl] = Field(None, max_length=200)
    phone_number: Optional[str] = Field(None, max_length=20)

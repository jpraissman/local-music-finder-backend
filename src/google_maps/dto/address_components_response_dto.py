from pydantic import BaseModel, Field, EmailStr, HttpUrl, model_validator
from datetime import date, time
from typing import List, Optional
from src.bands.types.band_types import BandType
from src.bands.types.genres import Genre
from src.events.types.band_or_venue import BandOrVenue


class AddressComponentsResponseDTO(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str
    county: str
    town: str

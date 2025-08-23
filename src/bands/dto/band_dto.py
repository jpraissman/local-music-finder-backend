from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import Optional, List
from src.bands.types.band_types import BandType
from src.bands.types.genres import Genre
from src.bands.models.band_model import Band as BandModel


class BandDTO(BaseModel):
    band_name: str = Field(..., max_length=50)
    band_type: BandType
    tribute_band_name: Optional[str] = Field("", max_length=100)
    genres: List[Genre]
    website_url: Optional[HttpUrl] = Field(None, max_length=200)
    facebook_url: Optional[HttpUrl] = Field(None, max_length=200)
    instagram_url: Optional[HttpUrl] = Field(None, max_length=200)
    id: int

    @model_validator(mode="after")
    def check_tribute_band_name(self):
        if self.band_type == BandType.TRIBUTE_BAND and len(self.tribute_band_name) == 0:
            raise ValueError("Tribute band name must be provided for tribute bands.")
        return self


# TODO: Throw exception here?
def transform_from_band_model(band_model: BandModel) -> BandDTO:
    band_dto = BandDTO(**band_model)
    return band_dto

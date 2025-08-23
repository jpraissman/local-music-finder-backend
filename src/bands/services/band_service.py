from src.bands.dto.upsert_band_request_dto import UpsertBandRequestDTO
from src.bands.dto.band_dto import BandDTO
from src.bands.models.band_model import Band as BandModel
from src.bands.dto.band_dto import transform_from_band_model
from app import db


def upsert_band(payload: UpsertBandRequestDTO) -> BandDTO:
    # Find existing band by band_name
    existing_band: BandModel = BandModel.query.filter_by(
        band_name=payload.band_name
    ).first()

    # If there is existing band, update the fields
    if existing_band != None:
        existing_band.band_type = payload.band_type
        existing_band.genres = payload.genres
        existing_band.tribute_band_name = payload.tribute_band_name
        if payload.website_url != None:
            existing_band.website_url = payload.website_url
        if payload.facebook_url != None:
            existing_band.facebook_url = payload.facebook_url
        if payload.instagram_url != None:
            existing_band.instagram_url = payload.instagram_url
        # TODO: Do we need db.commit here?
        band_dto = transform_from_band_model(existing_band)
    # If there is no existing band, create one
    else:
        band_dto = BandDTO(**payload)

        # Add to the database
        band = BandModel(band_dto)
        db.session.add(band)

    db.session.commit()  # TODO: Should the commit be done here? Also should db be passed into the function? Or accessed through a helper or something

    return band_dto

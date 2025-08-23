from src.venues.dto.upsert_venue_request_dto import UpsertVenueRequestDTO
from src.venues.dto.venue_dto import VenueDTO
from src.venues.dto.venue_dto import transform_from_venue_model
import src.google_maps.services.google_maps_service as GoogleMapsService
from app import db
from src.venues.models.venue_model import Venue as VenueModel


def upsert_venue(payload: UpsertVenueRequestDTO) -> VenueDTO:
    # Find existing venue by venue_name and place_id
    existing_venue: VenueModel = VenueModel.query.filter_by(
        venue_name=payload.venue_name, place_id=payload.venue_place_id
    ).first()

    # If there is existing venue, update the fields
    if existing_venue != None:
        if payload.phone_number != None:
            existing_venue.phone_number = payload.phone_number
        if payload.website_url != None:
            existing_venue.website_url = payload.website_url
        if payload.facebook_url != None:
            existing_venue.facebook_url = payload.facebook_url
        if payload.instagram_url != None:
            existing_venue.instagram_url = payload.instagram_url
        # TODO: Do we need db.commit here?
        venue_dto = transform_from_venue_model(existing_venue)
    # If there is no existing venue, create one
    else:
        address_componenets = GoogleMapsService.get_address_components(
            place_id=payload.venue_place_id
        )
        venue_dto = VenueDTO(**payload, **address_componenets)

        # Add to the database
        venue = VenueModel(venue_dto)
        db.session.add(venue)

    db.session.commit()  # TODO: Should the commit be done here? Also should db be passed into the function? Or accessed through a helper or something

    return venue_dto

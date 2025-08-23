import src.venues.services.venue_service as VenueService
from src.venues.dto.upsert_venue_request_dto import UpsertVenueRequestDTO
from src.events.dto.create_event_response_dto import CreateEventResponseDTO
from src.events.dto.create_event_request_dto import CreateEventRequestDTO
from src.events.types.band_or_venue import BandOrVenue
from src.bands.dto.upsert_band_request_dto import UpsertBandRequestDTO
import src.bands.services.band_service as BandService
from src.events.dto.event_dto import EventDTO
import string, random
from src.events.models.event_model import Event as EventModel
from app import db


def create_event(payload: dict) -> CreateEventResponseDTO:
    try:
        event_request = CreateEventRequestDTO(**payload)
    except Exception as e:
        pass  # HANDLE EXCEPTION HERE

    # Upsert the venue
    venue_request = UpsertVenueRequestDTO(
        **payload,
        website_url=(
            event_request.website_url
            if event_request.band_or_venue == BandOrVenue.VENUE
            else None
        ),
        facebook_url=(
            event_request.facebook_url
            if event_request.band_or_venue == BandOrVenue.VENUE
            else None
        ),
        instagram_url=(
            event_request.instagram_url
            if event_request.band_or_venue == BandOrVenue.VENUE
            else None
        )
    )
    venue = VenueService.upsert_venue(venue_request)

    # Upsert the band
    band_request = UpsertBandRequestDTO(
        **payload,
        website_url=(
            event_request.website_url
            if event_request.band_or_venue == BandOrVenue.BAND
            else None
        ),
        facebook_url=(
            event_request.facebook_url
            if event_request.band_or_venue == BandOrVenue.BAND
            else None
        ),
        instagram_url=(
            event_request.instagram_url
            if event_request.band_or_venue == BandOrVenue.BAND
            else None
        )
    )
    band = BandService.upsert_band(band_request)

    # Create the event
    event_id = _generate_event_id()
    event_dto = EventDTO(
        **payload, venue_id=venue.id, band_id=band.id, event_id=event_id
    )
    event = EventModel(event_dto)
    db.session.add(event)
    db.session.commit()

    return CreateEventResponseDTO(event_id=event_id)


# Generates a random 8 character event id
def _generate_event_id() -> str:
    # Generate random id
    unique_id_found = False
    while not unique_id_found:
        characters = string.ascii_letters + string.digits
        new_event_id = "".join(random.choice(characters) for _ in range(8))
        try:
            EventModel.query.filter_by(event_id=new_event_id).one()
            unique_id_found = False
        except:
            unique_id_found = True
    return new_event_id

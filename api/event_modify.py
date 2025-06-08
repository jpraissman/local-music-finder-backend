# This file represents all the api routes that can modify events

from app import db, executor
from flask import Blueprint, jsonify, request
from scripts.models.event import Event, format_event_input
import scripts.send_emails as EmailSender
from scripts.models.venue import Venue
from scripts.models.band import Band
from scripts.generate_event_id import generate_event_id 

event_modify_bp = Blueprint('event_modify', __name__)

# Background event to run after an event is created.
def create_event_background(eventId: str):
  # Get the event
  event: Event = Event.query.filter_by(event_id=eventId).one()

  # Send email confirming event creation and giving Event ID
  email_1_status = EmailSender.send_event_email(event)

  # Send email about event creation to admins
  email_2_status = EmailSender.send_admin_event_email(event)

  # Get any events with the same date and address. If there are potential duplicates, send an email
  events = db.session.query(Event).join(Event.venue).filter(Event.event_date == event.event_date,
                                                            Venue.place_id == event.venue.place_id).all()
  email_3_status = True
  if (len(events) > 1):
    email_3_status = EmailSender.send_duplicate_event_email(events)

  # Confirm all emails were sent properly
  if (email_1_status and email_2_status and email_3_status):
    Event.query.filter_by(event_id=event.event_id).update(dict(email_sent=True))
    db.session.commit()

# Used to get the related venue when creating/updating events. Handles adding the venue to
# the database.
def get_related_venue(input: dict[str: any]):
  # Lookup if there is a venue already in the database
  related_venue: Venue = Venue.query.filter_by(venue_name=input["venue_name"], place_id=input["venue_place_id"]).first()
  if related_venue == None:
    # There is no related venue, so we need to create one
    related_venue = Venue(venue_name=input["venue_name"], 
                          place_id=input["venue_place_id"],
                          phone_number=input["phone_number"] if input["phone_number"] != "" else None,
                          facebook_url=input["facebook_handle"] if input["facebook_handle"] != "" else None,
                          instagram_url=input["instagram_handle"] if input["instagram_handle"] != "" else None,
                          website_url=input["website"] if input["website"] != "" else None)
    db.session.add(related_venue)
    db.session.commit()
  else:
    # There is a related venue, so we need to update it
    related_venue.phone_number = input["phone_number"] if input["phone_number"] != "" else related_venue.phone_number
    related_venue.facebook_url = input["facebook_handle"] if input["facebook_handle"] != "" else related_venue.facebook_url
    related_venue.instagram_url = input["instagram_handle"] if input["instagram_handle"] != "" else related_venue.instagram_url
    related_venue.website_url = input["website"] if input["website"] != "" else related_venue.website_url
    db.session.commit()
  return related_venue

# Used to get the related band when creating/updating events. Handles adding the band to
# the database and updating it accordingly.
def get_related_band(input: dict[str: any]):
  related_band: Band = Band.query.filter_by(band_name=input["band_name"]).first()
  if related_band == None:
    # There is no related band, so we need to create one
    related_band = Band(band_name=input["band_name"], band_type=input["band_type"], 
                        tribute_band_name=input["tribute_band_name"], genres=input["genres"])
    db.session.add(related_band)
    db.session.commit()
  else:
    # There is a related band, so we need to update it
    related_band.band_name = input["band_name"]
    related_band.band_type = input["band_type"]
    related_band.tribute_band_name = input["tribute_band_name"]
    related_band.genres = input["genres"]
    db.session.commit()
  return related_band

# Create an Event
@event_modify_bp.route('/events', methods = ['POST'])
def create_event():
  # Generate event id
  new_event_id = generate_event_id()

  # Format the input correctly
  input = format_event_input(request)

  related_venue = get_related_venue(input)
  related_band = get_related_band(input)

  # Create the event
  event = Event(band_name = input["band_name"], 
                band_type = input["band_type"], 
                tribute_band_name = input["tribute_band_name"], 
                genres = input["genres"], 
                event_date = input["event_date"], 
                start_time = input["start_time"], 
                end_time = input["end_time"],
                cover_charge = input["cover_charge"], 
                other_info = input["other_info"], 
                facebook_handle = input["facebook_handle"], 
                instagram_handle = input["instagram_handle"], 
                website = input["website"], 
                band_or_venue = input["band_or_venue"], 
                phone_number = input["phone_number"], 
                event_id = new_event_id, 
                email_address = input["email_address"],
                venue_id=related_venue.id,
                band_id=related_band.id)
  db.session.add(event)
  db.session.commit()

  # Run the background tasks
  executor.submit(create_event_background, event.event_id)
  
  return jsonify({'event': event.get_metadata()})

# edit an event
@event_modify_bp.route('/events/<event_id>', methods = ['PUT'])
def update_event(event_id):
  event = Event.query.filter_by(event_id=event_id)

  # Format the input correctly
  input = format_event_input(request)

  related_venue = get_related_venue(input)
  related_band = get_related_band(input)

  event.update(dict(band_name = input["band_name"], 
                  band_type = input["band_type"], 
                  tribute_band_name = input["tribute_band_name"], 
                  genres = input["genres"], 
                  event_date = input["event_date"], 
                  start_time = input["start_time"], 
                  end_time = input["end_time"],
                  cover_charge = input["cover_charge"], 
                  other_info = input["other_info"], 
                  facebook_handle = input["facebook_handle"], 
                  instagram_handle = input["instagram_handle"], 
                  website = input["website"], 
                  band_or_venue = input["band_or_venue"], 
                  phone_number = input["phone_number"], 
                  email_address = input["email_address"],
                  venue_id=related_venue.id,
                  band_id=related_band.id))
  db.session.commit()
  return f'Event (id: {event_id}) updated!'

# delete an event
@event_modify_bp.route('/events/<event_id>', methods = ['DELETE'])
def delete_event(event_id):
  event = Event.query.filter_by(event_id=event_id).one()
  db.session.delete(event)
  db.session.commit()
  return jsonify({'message': 'Event (id: {event_id}) deleted!'})
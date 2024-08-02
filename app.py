# Import External Modules
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import time
from date_ranges import get_date_range
from max_distance import get_max_distance_meters
import random
import string
import os

# Create important server stuff
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# Import Internal Modules
from event import Event
# from send_event_email import send_event_email


# Create an event
# Conditions:
#    - event_date must be a String in the format "2024-01-01" or "2020-11-24".
#    - start_time/end_time must be a String in the format "06:30" or "19:00". 
@app.route('/events', methods = ['POST'])
def create_event():
  venue_name = request.json['venue_name']
  band_name = request.json['band_name']
  band_type = request.json['band_type']
  tribute_band_name = request.json['tribute_band_name']
  genres = request.json['genres']
  event_date = request.json['event_date']
  start_time = request.json['start_time']
  end_time = request.json['end_time']
  address_id = request.json['address_id']
  cover_charge = request.json['cover_charge']
  other_info = request.json['other_info']
  facebook_handle = request.json['facebook_handle']
  instagram_handle = request.json['instagram_handle']
  website = request.json['website']
  band_or_venue = request.json['band_or_venue']
  phone_number = request.json['phone_number']
  address_description = request.json['address_description']
  email_address = request.json['email_address']

  # Generate random id
  unique_id_found = False
  while not unique_id_found: 
    characters = string.ascii_letters + string.digits
    new_event_id = ''.join(random.choice(characters) for _ in range(8))

    try:
      Event.query.filter_by(event_id=new_event_id).one()
      unique_id_found = False
    except:
      unique_id_found = True

  event = Event(venue_name, band_name, band_type, tribute_band_name, genres, event_date, start_time, 
                end_time, address_id, cover_charge, other_info, facebook_handle, instagram_handle, 
                website, band_or_venue, phone_number, address_description, new_event_id, email_address)
  db.session.add(event)
  db.session.commit()
  # Send email confirming event confirmation and giving Event ID
  # send_event_email(event)
  return {'event': event.get_metadata()}

@app.route('/events', methods= ['GET'])
def get_events():
  # Get filter values
  date_range = request.args.get('date_range')
  address_id = request.args.get('address_id')
  max_distance = request.args.get('max_distance')
  genres = request.args.get('genres')
  band_types = request.args.get('band_types')

  # Get Date Range
  start_date, end_date = get_date_range(date_range)
  # Genres
  genres = genres.split("/")
  # Band Types
  band_types = band_types.split("/")
  # Max Distance
  max_distance = get_max_distance_meters(max_distance)

  # Get events that meet the filter requirements
  events = Event.query.filter(Event.band_type.in_(band_types),
                              Event.event_date >= start_date,
                              Event.event_date <= end_date).all()
  event_list = []
  for event in events:
    added = False
    for genre in genres:
       if not added and genre in event.genres:
          # Need Error Handling here, in case response was bad
          event.set_distance_data(address_id)
          if (event.distance_value <= max_distance):
            event_list.append(event.get_all_details())
            added = True
    
  return {'events': event_list}

# get single event
@app.route('/events/<event_id>', methods = ['GET'])
def get_event(event_id):
  try:
    event = Event.query.filter_by(event_id=event_id).one()
    return {'event': event.get_all_details()}
  except:
    return "Invalid ID", 400
  

# delete an event
@app.route('/events/<event_id>', methods = ['DELETE'])
def delete_event(event_id):
  event = Event.query.filter_by(event_id=event_id).one()
  db.session.delete(event)
  db.session.commit()
  return f'Event (id: {event_id}) deleted!'

# edit an event
@app.route('/events/<event_id>', methods = ['PUT'])
def update_event(event_id):
  event = Event.query.filter_by(event_id=event_id)

  venue_name = request.json['venue_name']
  band_name = request.json['band_name']
  band_type = request.json['band_type']
  tribute_band_name = request.json['tribute_band_name']
  genres = request.json['genres']
  event_date = request.json['event_date']
  start_time = request.json['start_time']
  end_time = request.json['end_time']
  address_id = request.json['address_id']
  cover_charge = request.json['cover_charge']
  other_info = request.json['other_info']
  facebook_handle = request.json['facebook_handle']
  instagram_handle = request.json['instagram_handle']
  website = request.json['website']
  band_or_venue = request.json['band_or_venue']
  phone_number = request.json['phone_number']
  address_description = request.json['address_description']
  event.update(dict(venue_name = venue_name, band_name = band_name, band_type = band_type,
                    tribute_band_name = tribute_band_name, genres = genres, event_date = event_date,
                    start_time = start_time, end_time = end_time, address_id = address_id,
                    cover_charge = cover_charge, other_info = other_info, facebook_handle = facebook_handle,
                    instagram_handle = instagram_handle, website = website, band_or_venue = band_or_venue,
                    phone_number = phone_number, address_description = address_description))
  db.session.commit()
  return f'Event (id: {event_id}) updated!'

if __name__ == '__main__':
  app.run()


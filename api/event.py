from flask import Blueprint, request, jsonify, Response, abort
from scripts.date_ranges import get_date_range
from scripts.max_distance import get_max_distance_miles
from scripts.haversine_distance import haversine_distance
import random, string, requests, csv, io, urllib.parse
import scripts.send_emails as EmailSender 
from datetime import datetime
from typing import List
from sqlalchemy import desc
from scripts.event import Event
from scripts.query import Query
from app import db, executor, API_KEY, ADMIN_KEY

event_bp = Blueprint('event', __name__)

# Background event to run after an event is created.
def create_event_background(event: Event):
  # Send email confirming event creation and giving Event ID
  email_1_status = EmailSender.send_event_email(event)

  # Send email about event creation to admins
  email_2_status = EmailSender.send_admin_event_email(event)

  # Get any events with the same date and address. If there are potential duplicates, send an email
  events = Event.query.filter(Event.event_date == event.event_date,
                              Event.address == event.address).all()
  email_3_status = True
  if (len(events) > 1):
    email_3_status = EmailSender.send_duplicate_event_email(events)

  # Confirm all emails were sent properly
  if (email_1_status and email_2_status and email_3_status):
    Event.query.filter_by(event_id=event.event_id).update(dict(email_sent=True))
    db.session.commit()

# Create an Event
@event_bp.route('/events', methods = ['POST'])
def create_event():
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

  # Create Event object and commit to the database
  event = Event(venue_name = request.json['venue_name'], 
                band_name = request.json['band_name'], 
                band_type = request.json['band_type'], 
                tribute_band_name = request.json['tribute_band_name'], 
                genres = request.json['genres'], 
                event_date = request.json['event_date'], 
                start_time = request.json['start_time'], 
                end_time = request.json['end_time'],
                address = request.json['address'],
                cover_charge = request.json['cover_charge'], 
                other_info = request.json['other_info'], 
                facebook_handle = request.json['facebook_handle'], 
                instagram_handle = request.json['instagram_handle'], 
                website = request.json['website'], 
                band_or_venue = request.json['band_or_venue'], 
                phone_number = request.json['phone_number'], 
                event_id = new_event_id, 
                email_address = request.json['email_address'])
  db.session.add(event)
  db.session.commit()

  # Run the background tasks
  if request.json['send_emails'] == "Yes":
    executor.submit(create_event_background, event)
  
  return {'event': event.get_metadata()}

# Get events (for main part of website)
@event_bp.route('/events', methods= ['GET'])
def get_events():
  # Get filter values
  date_range = request.args.get('date_range')
  address = request.args.get('address')
  max_distance = request.args.get('max_distance')
  genres = request.args.get('genres')
  band_types = request.args.get('band_types')
  from_where = request.args.get('from_where')

  start_date, end_date = get_date_range(date_range)
  genres = genres.split("::")
  band_types = band_types.split("::")
  max_distance = get_max_distance_miles(max_distance)

  # Get long and lat using address
  encoded_address = urllib.parse.quote(address)
  url = f'https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}'
  response = requests.get(url)
  response.raise_for_status()
  data = response.json()["results"][0]["geometry"]["location"]
  lat = data["lat"]
  lng = data["lng"]

  # Get events that meet the filter requirements
  potential_events = Event.query.filter(Event.band_type.in_(band_types),
                                        Event.event_date >= start_date,
                                        Event.event_date <= end_date).all()
  final_events = []
  for potential_event in potential_events:
    for genre in genres:
       if genre in potential_event.genres:
          distance = haversine_distance(lat, potential_event.lat, lng, potential_event.lng)
          if (distance <= max_distance):
            potential_event.set_distance_data(str(round(distance, 1)) + " mi", round(distance, 2))
            final_events.append(potential_event.get_all_details(False, False))
          break

  # Create a row in the 'Query' table for this query.
  max_distance_orig = request.args.get('max_distance')
  query = Query(date_range, address, max_distance_orig, genres, band_types, from_where)
  db.session.add(query)
  db.session.commit()

  # Sort the event_list by event_datetime
  event_list_sorted = sorted(final_events, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': event_list_sorted}

# Get events with the given ids
@event_bp.route('/events/ids', methods = ['GET'])
def get_events_by_id():
  ids = request.args.get('ids').split("::")

  events = Event.query.filter(Event.id.in_(ids))
  
  events_json = []
  for event in events:
    event.set_distance_data("", -1)
    events_json.append(event.get_all_details(False, False))

  events_json_sorted = sorted(events_json, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}

# Get a CSV file of all events for admins
@event_bp.route('/all-events', methods= ['GET'])
def get_all_events():
  admin_key = request.args.get('admin_key')
  if (admin_key != ADMIN_KEY):
    abort(403)

  # Step 1: Create an in-memory string buffer
  csv_buffer = io.StringIO()

  # Step 2: Use the csv writer to write to the buffer
  writer = csv.writer(csv_buffer)
  writer.writerow(['Venue', 'Band', 'Type', 'Start Time',
                   'End Time', 'Cover Charge', 'Event Date',
                   'Address', 'County', 'Genres', 'Tribute Band Name',
                   'Other Info', 'Facebook', 'Instagram',
                   'Website', "Phone", 'Band/Venue',
                   'Email Address', 'Created Date', 'Id', 
                   'Event Id'])  # CSV header

  events: List[Event] = Event.query.order_by(desc(Event.created_date)).all()
  for event in events:
    writer.writerow([event.venue_name, event.band_name, event.band_type, event.start_time,
                     event.end_time, event.cover_charge, event.event_date,
                     event.address, event.county, event.genres, event.tribute_band_name, 
                     event.other_info, event.facebook_handle, event.instagram_handle,
                     event.website, event.phone_number, event.band_or_venue,
                     event.email_address, event.created_date, event.id,
                     event.event_id])

  # Step 3: Set the buffer's position to the start (so it can be read)
  csv_buffer.seek(0)

  # Step 4: Create a Flask Response, passing the CSV data as content
  response = Response(csv_buffer.getvalue(), mimetype='text/csv')

  # Step 5: Set the content-disposition header to prompt a download
  response.headers['Content-Disposition'] = 'attachment; filename=Events.csv'

  return response

# Get events based on given created date/event date (for admin site)
@event_bp.route('/events-admin', methods= ['GET'])
def get_events_admin():
  # Get filter values
  event_date = request.args.get('event_date')
  created_date = request.args.get('created_date')

  # Get Event Date Info
  if event_date == "All":
    event_start_date = datetime.strptime("01/01/1900", "%m/%d/%Y").date()
    event_end_date = datetime.strptime("01/01/2100", "%m/%d/%Y").date()
  else:
    event_start_date = datetime.strptime(event_date, "%m/%d/%Y").date()
    event_end_date = datetime.strptime(event_date, "%m/%d/%Y").date()

  # Get Created Date Info
  if created_date == "All":
    created_start_date = datetime.strptime("01/01/1900", "%m/%d/%Y")
    created_end_date = datetime.strptime("01/01/2100", "%m/%d/%Y")
  else:
    created_start_date = datetime.strptime(created_date, "%m/%d/%Y")
    created_end_date = datetime.strptime(created_date, "%m/%d/%Y")

  # Get events that meet the filter requirements
  events = Event.query.filter(Event.event_date >= event_start_date,
                              Event.event_date <= event_end_date,
                              Event.created_date >= created_start_date,
                              Event.created_date <= created_end_date).all()
  event_list = []
  for event in events:
    event_list.append(event.get_all_details(True, True))

  # Determine text to display
  if (event_date == "All" and created_date == "All"):
    display_text = f"Showing all events occuring today or after"
  elif (event_date == "All"):
    display_text = f"Showing all events created on {created_start_date.strftime("%B %d, %Y")}"
  else:
    display_text = f"Showing all events occuring on {event_start_date.strftime("%B %d, %Y")}"
    
  return {'display_text': display_text, 'events': event_list}

# get single event
@event_bp.route('/events/<event_id>', methods = ['GET'])
def get_event(event_id):
  try:
    event = Event.query.filter_by(event_id=event_id).one()
    return {'event': event.get_all_details(False, False)}, 200
  except:
    return jsonify("Invalid ID"), 400

# Get all events in the next 30 days in the given county 
@event_bp.route('/events/county/<county_name>', methods = ['GET'])
def get_events_by_county(county_name):
  start_date, end_date = get_date_range('Next 30 Days')
  events = Event.query.filter(Event.county == county_name,
                              Event.event_date >= start_date,
                              Event.event_date <= end_date)
  
  events_json = []
  for event in events:
    event.set_distance_data("", -1)
    events_json.append(event.get_all_details(False, False))

  events_json_sorted = sorted(events_json, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}

  
# get all events this week
@event_bp.route('/events/all-events-this-week', methods = ['GET'])
def get_all_future_events():
  start_date, end_date = get_date_range("This Week (Mon-Sun)")
  events = Event.query.filter(Event.event_date >= start_date, 
                              Event.event_date <= end_date)
  
  all_event_details = []
  for event in events:
    all_event_details.append(event.get_all_details(False, False))

  events_json_sorted = sorted(all_event_details, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}
  

# delete an event
@event_bp.route('/events/<event_id>', methods = ['DELETE'])
def delete_event(event_id):
  event = Event.query.filter_by(event_id=event_id).one()
  db.session.delete(event)
  db.session.commit()
  return f'Event (id: {event_id}) deleted!'

# edit an event
@event_bp.route('/events/<event_id>', methods = ['PUT'])
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
  address = request.json['address']
  cover_charge = request.json['cover_charge']
  other_info = request.json['other_info']
  facebook_handle = request.json['facebook_handle']
  instagram_handle = request.json['instagram_handle']
  website = request.json['website']
  band_or_venue = request.json['band_or_venue']
  phone_number = request.json['phone_number']
  event.update(dict(venue_name = venue_name, band_name = band_name, band_type = band_type,
                    tribute_band_name = tribute_band_name, genres = genres, event_date = event_date,
                    start_time = start_time, end_time = end_time, address = address,
                    cover_charge = cover_charge, other_info = other_info, facebook_handle = facebook_handle,
                    instagram_handle = instagram_handle, website = website, band_or_venue = band_or_venue,
                    phone_number = phone_number))
  db.session.commit()
  return f'Event (id: {event_id}) updated!'

# Get events whose email has not been sent (for admin site)
@event_bp.route('/email-errors', methods= ['GET'])
def get_email_error_events():
  # Get events that meet the filter requirements
  events = Event.query.filter(Event.email_sent == False).all()
  event_list = []
  for event in events:
    event_list.append(event.get_all_details(True, True))
    
  return {'events': event_list}

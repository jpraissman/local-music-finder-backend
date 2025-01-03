from flask import Flask, request, jsonify, Response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import time
from scripts.date_ranges import get_date_range
from scripts.max_distance import get_max_distance_miles
from scripts.haversine_distance import haversine_distance
import random
import string
import os
import scripts.send_emails as EmailSender
from flask_executor import Executor
from datetime import datetime
from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
import traceback
import json
import time
import requests
from typing import List
import csv
import io
from flask_migrate import Migrate
import urllib.parse
from sqlalchemy import desc

# Create important server stuff
app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url.startswith("postgres:"):
  database_url = database_url.replace("postgres:", "postgresql:", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
executor = Executor(app)
limiter = Limiter(app=app, 
                  key_func=lambda: "global", 
                  default_limits=["100 per minute"])

# Must be imported after to avoid circular import
from scripts.event import Event
from scripts.query import Query
from scripts.visit import Visit
# from scripts.user import User

API_KEY = os.environ.get('API_KEY')
ADMIN_KEY = os.environ.get('ADMIN_KEY')

# Used to make helper send rate limit emails
class RateLimitEmailHelper:
  email_sent = False

# Custom 404 error handler
@app.errorhandler(404)
def not_found(error):
    # Return an empty response
    return Response(status=200)

@app.errorhandler(Exception)
def handle_exception(e):
  print("Handling Error")

  tb = traceback.format_exc()

  request_info = {
    "method": request.method,
    "url": request.url,
    "headers": dict(request.headers),
    "body": request.get_data(as_text=True)
  }

  response = {
    "error": {
      "type": type(e).__name__,
      "message": str(e),
      "traceback": tb
    },
    "request": request_info,
    "path": request.path
  }

  EmailSender.send_error_occurred_email(json.dumps(response, indent=8))
  return jsonify(response), 500

# Handles rate limit errors by sending an email alerting that a rate limit has been hit
@app.errorhandler(429)
def handle_rate_limit_exception(e):
  print("Handling Rate Limit Error")
  if not RateLimitEmailHelper.email_sent:
    EmailSender.send_error_occurred_email("The API limit was hit: Too many requests in the last minute have been made (Over 100 requests).")
    RateLimitEmailHelper.email_sent = True
    executor.submit(reset_rate_limit_email)
    print("Sent email and submitted reset request")
  
  return jsonify("Too many requests have been made in the last minute"), 429

# Resets rate limit email so emails can be sent again when the application hits a rate limit.
def reset_rate_limit_email():
  time.sleep(1200)
  RateLimitEmailHelper.email_sent = False
  print("Reset rate limit email")


# Background events to run after an event is created.
def create_event_background(event: Event):
  print("Starting background events")
  # Send email confirming event confirmation and giving Event ID
  print("Sending Event Confirmation")
  email_1_status = EmailSender.send_event_email(event)
  if email_1_status:
    print("Sent")

  # Send email about even confirmation to admins
  print("Sending Admin Email")
  email_2_status = EmailSender.send_admin_event_email(event)
  if email_2_status:
    print("Sent")

  # Get any events with the same date and address. If there are potential duplicates, send an email
  events = Event.query.filter(Event.event_date == event.event_date,
                              Event.address == event.address).all()
  
  email_3_status = True
  if (len(events) > 1):
    print("Sending duplicate email")
    email_3_status = EmailSender.send_duplicate_event_email(events)
    if email_3_status:
      print("Sent")

  if (email_1_status and email_2_status and email_3_status):
    print("Updating event to say emails were sent")
    Event.query.filter_by(event_id=event.event_id).update(dict(email_sent=True))
    db.session.commit()
    print("Updated")
  
  print("Finished background stuff")

# Create a Visit
@app.route('/visit', methods = ['POST'])
def create_visit():
  page = request.json['page']
  from_where = request.json['from']
  user_id = request.json['user']

  visit = Visit(page, from_where, user_id)
  db.session.add(visit)
  db.session.commit()

  return "Visit Created"

# Create an Event
@app.route('/events', methods = ['POST'])
def create_event():
  # Get all variables from body of request
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
  email_address = request.json['email_address']
  send_emails = request.json['send_emails']

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
  event = Event(venue_name, band_name, band_type, tribute_band_name, genres, event_date, start_time, 
                end_time, address, cover_charge, other_info, facebook_handle, instagram_handle, 
                website, band_or_venue, phone_number, new_event_id, email_address)
  db.session.add(event)
  db.session.commit()

  # Run the background tasks of the event creation (duplicate checking and email confirmation)
  if send_emails == "Yes":
    executor.submit(create_event_background, event)
  
  return {'event': event.get_metadata()}

# Get events (for main part of website)
@app.route('/events', methods= ['GET'])
def get_events():
  # Get filter values
  date_range = request.args.get('date_range')
  address = request.args.get('address')
  max_distance = request.args.get('max_distance')
  genres = request.args.get('genres')
  band_types = request.args.get('band_types')
  from_where = request.args.get('from_where')

  # Get Date Range
  start_date, end_date = get_date_range(date_range)
  # Genres
  genres = genres.split("::")
  # Band Types
  band_types = band_types.split("::")
  # Max Distance
  max_distance = get_max_distance_miles(max_distance)

  # Get long and lat using address
  encoded_address = urllib.parse.quote(address)
  url = f'https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}'
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for 4xx/5xx errors

    data = response.json()["results"][0]["geometry"]["location"]
    lat = data["lat"]
    lng = data["lng"]
  except Exception as e:
    print(f"Error getting long and lat: {e}")

  # Get events that meet the filter requirements
  all_events = Event.query.filter(Event.band_type.in_(band_types),
                              Event.event_date >= start_date,
                              Event.event_date <= end_date).all()
  all_final_events = []
  for event in all_events:
    added = False
    for genre in genres:
       if not added and genre in event.genres:
          added = True
          distance = haversine_distance(lat, event.lat, lng, event.lng)
          if (distance <= max_distance):
            event.set_distance_data(str(round(distance, 1)) + " mi", round(distance, 2))
            all_final_events.append(event.get_all_details(False, False))

  # Create a row in the 'Query' table for this query.
  max_distance = request.args.get('max_distance')
  query = Query(date_range, address, max_distance, genres, band_types, from_where)
  db.session.add(query)
  db.session.commit()

  # Sort the event_list by event_datetime
  event_list_sorted = sorted(all_final_events, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': event_list_sorted}

@app.route('/events/ids', methods = ['GET'])
def get_events_by_id():
  event_ids_raw = request.args.get('ids')
  event_ids = event_ids_raw.split("::")

  events = Event.query.filter(Event.id.in_(event_ids))
  
  events_json = []
  for event in events:
    event.set_distance_data("", -1)
    events_json.append(event.get_all_details(False, False))

  events_json_sorted = sorted(events_json, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}

# Get a CSV file of all events for admins
@app.route('/all-events', methods= ['GET'])
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
                   'Address', 'Genres', 'Tribute Band Name',
                   'Other Info', 'Facebook', 'Instagram',
                   'Website', "Phone", 'Band/Venue',
                   'Email Address', 'Created Date', 'Id', 
                   'Event Id'])  # CSV header

  events: List[Event] = Event.query.order_by(desc(Event.created_date)).all()
  for event in events:
    writer.writerow([event.venue_name, event.band_name, event.band_type, event.start_time,
                     event.end_time, event.cover_charge, event.event_date,
                     event.address, event.genres, event.tribute_band_name, 
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

# Get a CSV file of all the queries
@app.route('/all-queries', methods= ['GET'])
def get_all_queries():
  # Step 1: Create an in-memory string buffer
  csv_buffer = io.StringIO()

  # Step 2: Use the csv writer to write to the buffer
  writer = csv.writer(csv_buffer)
  writer.writerow(['Search Date', 'Date Range', 'Location', 'Distance',
                   'Genres', 'Band Types', 'From', 'Id'])  # CSV header

  queries: List[Query] = Query.query.order_by(desc(Query.created_at)).all()
  for query in queries:
    writer.writerow([query.created_at, query.time_range, query.location,
                     query.distance, query.genres, query.band_types, query.from_where, query.id])

  # Step 3: Set the buffer's position to the start (so it can be read)
  csv_buffer.seek(0)

  # Step 4: Create a Flask Response, passing the CSV data as content
  response = Response(csv_buffer.getvalue(), mimetype='text/csv')

  # Step 5: Set the content-disposition header to prompt a download
  response.headers['Content-Disposition'] = 'attachment; filename=searches.csv'

  return response

# Get a CSV file of all the visits
@app.route('/all-visits', methods= ['GET'])
def get_all_visits():
  # Step 1: Create an in-memory string buffer
  csv_buffer = io.StringIO()

  # Step 2: Use the csv writer to write to the buffer
  writer = csv.writer(csv_buffer)
  writer.writerow(['Visit Date', 'Page', 'From', 'User'])  # CSV header

  visits: List[Visit] = Visit.query.order_by(desc(Visit.created_at)).all()
  for visit in visits:
    writer.writerow([visit.created_at, visit.page, visit.from_where, visit.user_id])

  # Step 3: Set the buffer's position to the start (so it can be read)
  csv_buffer.seek(0)

  # Step 4: Create a Flask Response, passing the CSV data as content
  response = Response(csv_buffer.getvalue(), mimetype='text/csv')

  # Step 5: Set the content-disposition header to prompt a download
  response.headers['Content-Disposition'] = 'attachment; filename=visits.csv'

  return response


# Get events whose email has not been sent (for admin site)
@app.route('/email-errors', methods= ['GET'])
def get_email_error_events():
  # Get events that meet the filter requirements
  events = Event.query.filter(Event.email_sent == False).all()
  event_list = []
  for event in events:
    event_list.append(event.get_all_details(True, True))
    
  return {'events': event_list}

# Get events based on given created date/event date (for admin site)
@app.route('/events-admin', methods= ['GET'])
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
@app.route('/events/<event_id>', methods = ['GET'])
def get_event(event_id):
  try:
    event = Event.query.filter_by(event_id=event_id).one()
    return {'event': event.get_all_details(False, False)}, 200
  except:
    return jsonify("Invalid ID"), 400
  
# get all events this week
@app.route('/events/all-events-this-week', methods = ['GET'])
def get_all_future_events():
  start_date, end_date = get_date_range("This Week (Mon-Sun)")
  events = Event.query.filter(Event.event_date >= start_date, 
                              Event.event_date <= end_date)
  
  all_event_details = []
  for event in events:
    all_event_details.append(event.get_all_details(False, False))

  return {'events': all_event_details}
  

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


# # Create a User that gets weekly event notifications
# @app.route('/users', methods = ['POST'])
# def create_user():
#   # Get all variables from body of request
#   email_address = request.json['email_address']
#   address_id = request.json['address_id']
#   max_distance = request.json['max_distance']
#   genres = request.json['genres']
#   band_types = request.json['band_types']
#   address_description = request.json['address_description']

#   # Convert max_distance into meters
#   max_distance_value = get_max_distance_meters(max_distance)

#   # Create Event object and commit to the database
#   user = User(email_address, address_id, max_distance, genres, band_types, address_description,
#               max_distance_value)
#   db.session.add(user)
#   db.session.commit()
  
#   return {"user: ": "User Created"}, 201

# # Send weekly event notifications to subscribed Users
# @app.route('/send-emails', methods = ['POST'])
# def send_weekly_emails():
#   # Get all variables from body of request
#   api_key = request.json['api_key']

#   users = User.query.filter(User.subscribed).all()

#   for user in users:
#     # Get Date Range
#     start_date, end_date = get_date_range("All Future Dates")

#     # Get events that meet the filter requirements
#     events = Event.query.filter(Event.band_type.in_(user.band_types),
#                                 Event.event_date >= start_date,
#                                 Event.event_date <= end_date).all()
#     matched_events = []
#     for event in events:
#       added = False
#       for genre in user.genres:
#         if not added and genre in event.genres:
#             # Need Error Handling here, in case response was bad
#             event.set_distance_data(user.address_id)
#             if (event.distance_value <= user.max_distance_value):
#               matched_events.append(event)
#               added = True

#     EmailSender.send_weekly_event_notification(user, matched_events)

#   return {"email-status: ": "Emails Sent"}, 201

if __name__ == '__main__':
  app.run()


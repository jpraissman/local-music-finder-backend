from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import time
from scripts.date_ranges import get_date_range
from scripts.max_distance import get_max_distance_meters
import random
import string
import os
import scripts.send_emails as EmailSender
from flask_executor import Executor
from datetime import datetime
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
import traceback
import json

# Create important server stuff
app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url.startswith("postgres:"):
  database_url = database_url.replace("postgres:", "postgresql:", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)
executor = Executor(app)
# limiter = Limiter(app=app, 
#                   key_func=lambda: "global", 
#                   default_limits=["300 per minute"])

# Must be imported after to avoid circular import
from scripts.event import Event
# from scripts.user import User

rate_limit_email_sent = False

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

# @app.errorhandler(429)
# def handle_rate_limit_exception():
#   print("Handling Rate Limit Error")
#   EmailSender.send_error_occurred_email("The API limit was hit: Too many requests in the last minute have been made.")

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

  # Get Date Range
  start_date, end_date = get_date_range(date_range)
  # Genres
  genres = genres.split("::")
  # Band Types
  band_types = band_types.split("::")
  # Max Distance
  max_distance = get_max_distance_meters(max_distance)

  # Get events that meet the filter requirements
  events = Event.query.filter(Event.band_type.in_(band_types),
                              Event.event_date >= start_date,
                              Event.event_date <= end_date).all()
  event_list = []
  error_occurred = False
  errors = []
  for event in events:
    added = False
    for genre in genres:
       if not added and genre in event.genres:
          added = True
          response = event.set_distance_data(address)
          if (response[0] and event.distance_value <= max_distance):
            event_list.append(event.get_all_details(False, False))
          else:
            error_occurred = True
            errors.append(response)

  if error_occurred:
    message_body = ""
    for error in errors:
      message_body += f"\n\nOrigin: {error[1]}\nDestination: {error[2]}\nResponse: {error[3]}"
    EmailSender.send_error_occurred_email(f"An error occured while fetching events.\n{message_body}")
    
  # Sort the event_list by event_datetime
  event_list_sorted = sorted(event_list, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': event_list_sorted}

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
    return {'event': event.get_all_details(False, False)}
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


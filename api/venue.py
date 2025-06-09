from flask import Blueprint, jsonify, request
from scripts.models.venue import Venue
from scripts.models.event import Event
from app import db
from datetime import datetime
from scripts.validate_admin import validate_admin_key

venue_bp = Blueprint('venue', __name__)

@venue_bp.route('/venues/merge', methods=['POST'])
@validate_admin_key
def merge_venues():
  venue_id_one = request.json['venue_id_one']
  venue_id_two = request.json['venue_id_two']
  venue_name = request.json['venue_name']

  venue_1: Venue = Venue.query.filter_by(id=venue_id_one).first_or_404()
  venue_2: Venue = Venue.query.filter_by(id=venue_id_two).first_or_404()

  if venue_1.id == venue_2.id:
    return jsonify({"error": "Cannot merge the same venue"}), 400
  
  if len(venue_1.events) >= len(venue_2.events):
    events_to_move = venue_2.events
    for event in events_to_move:
      event.venue = venue_1
    db.session.commit()
    db.session.delete(venue_2)
    venue_1.venue_name = venue_name
  else:
    events_to_move = venue_1.events
    for event in events_to_move:
      event.venue = venue_2
    db.session.commit()
    db.session.delete(venue_1)
    venue_2.venue_name = venue_name
  db.session.commit()

  return jsonify({"message": "Venues merged successfully"}), 200

# Returns a dictionary with the keys being all the venue names and the values including the address and the place_id
@venue_bp.route('/venues', methods = ['GET'])
def get_all_venues():
  all_venues: list[Venue] = Venue.query.all()
  response: dict[str, dict[str, str]] = {}

  for venue in all_venues:
    response[venue.venue_name] = {"address": venue.address, "place_id": venue.place_id}

  return jsonify(response)

@venue_bp.route('/venues-for-nav-bar', methods = ['GET'])
def get_venues_for_nav_bar():
  all_venues: list[Venue] = Venue.query.all()
  response = []

  for venue in all_venues:
    response.append({"name": venue.venue_name, "town": venue.town, "id": venue.id})

  return jsonify(response)

@venue_bp.route('/venue/<venue_id>', methods = ['GET'])
def get_venue_details(venue_id):
  venue: Venue = Venue.query.filter_by(id=venue_id).first()
  if not venue:
    return jsonify({"error": "Venue not found"}), 404
  
  venue_details = {
    "id": venue.id,
    "name": venue.venue_name,
    "address": venue.address,
    "town": venue.town,
    "phone_number": venue.phone_number,
    "facebook_link": venue.facebook_url,
    "instagram_link": venue.instagram_url,
    "website": venue.website_url,
  }
  return jsonify(venue_details)

@venue_bp.route('/venue/<venue_id>/events', methods = ['GET'])
def get_venue_events(venue_id):
  events = db.session.query(Event).join(Event.venue).filter(Venue.id == venue_id).all()

  events_json = []
  for event in events:
    event.set_distance_data("", -1)
    events_json.append(event.get_all_details(False, False))

  events_json_sorted = sorted(events_json, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}
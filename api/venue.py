from flask import Blueprint, jsonify
from scripts.models.venue import Venue
from scripts.models.event import Event
from app import db
from datetime import datetime

venue_bp = Blueprint('venue', __name__)

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

@venue_bp.route('/venue/<venue_id>/events', methods = ['GET'])
def get_venue_events(venue_id):
  events = db.session.query(Event).join(Event.venue).filter(Venue.id == venue_id).all()

  events_json = []
  for event in events:
    event.set_distance_data("", -1)
    events_json.append(event.get_all_details(False, False))

  events_json_sorted = sorted(events_json, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}
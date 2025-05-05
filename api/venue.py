from flask import Blueprint, jsonify
from scripts.models.venue import Venue

venue_bp = Blueprint('venue', __name__)

# Returns a dictionary with the keys being all the venue names and the values including the address and the place_id
@venue_bp.route('/venues', methods = ['GET'])
def get_all_venues():
  all_venues: list[Venue] = Venue.query.all()
  response: dict[str, dict[str, str]] = {}

  for venue in all_venues:
    response[venue.venue_name] = {"address": venue.address, "place_id": venue.place_id}

  return jsonify(response)

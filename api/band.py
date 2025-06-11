from flask import Blueprint, jsonify, request
from app import db
from scripts.models.band import Band
from scripts.models.event import Event
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime

band_bp = Blueprint('band', __name__)

# Returns a dictionary with the keys being all the bands names and the values including the band type, tribute band name, and genres.
@band_bp.route('/bands', methods = ['GET'])
def get_all_bands():
  all_bands: list[Band] = Band.query.all()
  response = {}

  for band in all_bands:
    response[band.band_name] = {"band_type": band.band_type, "tribute_band_name": band.tribute_band_name, "genres": band.genres, "id": band.id}

  return jsonify(response)

@band_bp.route('/bands/add-video/<band_id>', methods = ['POST'])
def add_video(band_id):
  # Get the band from the database
  band: Band = Band.query.get(band_id)
  if not band:
    return jsonify({"error": "Band not found"}), 404

  # Get the video URL from the request
  video_url = request.json.get('video_url')
  if not video_url:
    return jsonify({"error": "Video URL is required"}), 400

  # Add the video ID to the band's list of YouTube IDs
  band.add_youtube_id(video_url)
  flag_modified(band, "youtube_ids")
  db.session.commit()

  return jsonify({"message": "Video added successfully"})

@band_bp.route('/bands-for-nav-bar', methods = ['GET'])
def get_bands_for_nav_bar():
  all_bands: list[Band] = Band.query.all()
  response = []

  for band in all_bands:
    response.append({"name": band.band_name, "genres": band.genres, "id": band.id,
                     "band_type": band.band_type, "tribute_band_name": band.tribute_band_name})

  return jsonify(response)

@band_bp.route('/band/<band_id>', methods = ['GET'])
def get_band_details(band_id):
  band: Band = Band.query.filter_by(id=band_id).first()
  if not band:
    return jsonify({"error": "Band not found"}), 404
  
  band_details = {
    "id": band.id,
    "name": band.band_name,
    "band_type": band.band_type,
    "tribute_band_name": band.tribute_band_name,
    "genres": band.genres,
    "facebook_url": band.facebook_url,
    "instagram_url": band.instagram_url,
    "website_url": band.website_url,
  }
  return jsonify(band_details)

@band_bp.route('/band/<band_id>/events', methods = ['GET'])
def get_band_events(band_id):
  events = db.session.query(Event).join(Event.band).filter(Band.id == band_id).all()

  events_json = []
  for event in events:
    event.set_distance_data("", -1)
    events_json.append(event.get_all_details(False, False))

  events_json_sorted = sorted(events_json, key=lambda x: datetime.fromisoformat(x["event_datetime"]))
  return {'events': events_json_sorted}

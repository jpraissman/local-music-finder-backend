from flask import Blueprint, jsonify
from scripts.models.band import Band

band_bp = Blueprint('band', __name__)

# Returns a dictionary with the keys being all the bands names and the values including the band type, tribute band name, and genres.
@band_bp.route('/bands', methods = ['GET'])
def get_all_bands():
  all_bands: list[Band] = Band.query.all()
  response = {}

  for band in all_bands:
    response[band.band_name] = {"band_type": band.band_type, "tribute_band_name": band.tribute_band_name, "genres": band.genres}

  return jsonify(response)

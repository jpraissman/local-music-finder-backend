from scripts.models.venue import Venue
import urllib.parse
import os
import requests
from app import db

API_KEY = os.environ.get('API_KEY')


venues: list[Venue] = Venue.query.all()

count = 0
for venue in venues:
  # Get long and lat using place_id
  encoded_address = urllib.parse.quote(venue.address)
  url = f'https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}'
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for 4xx/5xx errors

    # Get long and lat
    geo_data = response.json()["results"][0]["geometry"]["location"]
    lat = geo_data["lat"]
    lng = geo_data["lng"]

    # Get county
    address_components = response.json()["results"][0]["address_components"]
    for component in address_components:
      if component['types'][0] == 'administrative_area_level_2':
        county = component['long_name']


    # Get formatted address
    formatted_address = response.json()["results"][0]["formatted_address"]

    # Get place_id
    place_id = response.json()["results"][0]["place_id"]

    venue.lat = lat
    venue.lng = lng
    venue.address = formatted_address
    venue.county = county
    venue.place_id = place_id

    db.session.commit()


    # print("Lat:", lat)
    # print("Long:", lng)
    # print("county:", county)
    # print("formatted_address:", formatted_address)
    # print("place_id:", place_id)



  except Exception as e:
    print(f"Error: {e}")

  if count % 10 == 0:
    print("Completed 10:", count)
  count += 1
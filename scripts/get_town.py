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

    address_components = response.json()["results"][0]["address_components"]
    for component in address_components:
      if component['types'][0] == 'locality':
        town = component['long_name']

    venue.town = town

    db.session.commit()

    # print("Added town:", venue.town)

  except Exception as e:
    print(f"Error: {e}")

  if count % 10 == 0:
    print("Completed 10:", count)
  count += 1
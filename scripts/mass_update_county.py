from scripts.event import Event
import requests, urllib.parse, os
from app import db

API_KEY = os.environ.get('API_KEY')

# events = Event.query.all()

# for event in events:
#   print(event.venue_name)

events = Event.query.all()

for event in events:
  encoded_address = urllib.parse.quote(event.address)
  url = f'https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}'
  response = requests.get(url)
  response.raise_for_status()  # Raise an exception for 4xx/5xx errors

  data = response.json()["results"][0]["address_components"]
  for d in data:
    if d['types'][0] == 'administrative_area_level_2':
      county = d['long_name']
      print(county)
      event_to_update = Event.query.filter(Event.id == event.id)
      event_to_update.update(dict(county=county))
      db.session.commit()
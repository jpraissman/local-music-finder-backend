from scripts.event import Event
import requests
import os
from app import db

API_KEY = os.environ.get('API_KEY')

events = Event.query.all()

for event in events:
  # Get long and lat using place_id
  url = f'https://maps.googleapis.com/maps/api/geocode/json?address={event.address}&key={API_KEY}'
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for 4xx/5xx errors

    data = response.json()["results"][0]["geometry"]["location"]
    event.lat = data["lat"]
    event.lng = data["lng"]
  except Exception as e:
    print(f"Error getting long and lat: {e}")

db.session.commit()

print("All events updated")
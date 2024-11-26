from app import db
import requests
import os

API_KEY = os.environ.get('API_KEY')

class EventDistance(db.Model):
  __tablename__ = "event_distance"
  id = db.Column(db.Integer, primary_key=True)
  event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
  location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
  distance = db.Column(db.Integer, nullable=False)
  distance_formatted = db.Column(db.String, nullable=False)
  location = db.relationship('Location', backref='e_distances')
  event = db.relationship('Event', backref='event_distances')

  def __init__(self, location, event):
    self.location_id = location.id
    self.event_id = event.id

    # Calculate the distance
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={location.location}&destinations={event.address}&units=imperial&key={API_KEY}'
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for 4xx/5xx errors

    data = response.json()
    
    # Check if the response contains valid data
    if data['status'] == 'OK':
      self.distance = data["rows"][0]["elements"][0]["distance"]["value"]
      self.distance_formatted = data["rows"][0]["elements"][0]["distance"]["text"]
    else:
      print(f"Error: {data['status']}")
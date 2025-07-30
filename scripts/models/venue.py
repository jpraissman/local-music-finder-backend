from app import db
import requests, os
from scripts.models.event import Event
from flask import abort
from sqlalchemy.orm import Mapped

API_KEY = os.environ.get('API_KEY')

class Venue(db.Model):
  __tablename__ = "venue"

  id: int = db.Column(db.Integer, primary_key=True)
  events: Mapped[list[Event]] = db.relationship("Event", back_populates="venue", cascade="all, delete-orphan")
  venue_name: str = db.Column(db.String, nullable=False)
  address: str = db.Column(db.String, nullable=False)
  lat: float = db.Column(db.Float, nullable=False)
  lng: float = db.Column(db.Float, nullable=False)
  county: str = db.Column(db.String, nullable=False)
  place_id : str = db.Column(db.String, nullable=False)
  town: str = db.Column(db.String, nullable=False)
  phone_number: str = db.Column(db.String)
  facebook_url: str = db.Column(db.String)
  instagram_url: str = db.Column(db.String)
  website_url: str = db.Column(db.String)

  def __init__(self, venue_name: str, place_id: str, phone_number: str = None,
               facebook_url: str = None, instagram_url: str = None, website_url: str = None):
    self.venue_name = venue_name
    self.place_id = place_id
    self.phone_number = phone_number
    self.facebook_url = facebook_url
    self.instagram_url = instagram_url
    self.website_url = website_url

    # Get long, lat, county, and formatted_address using the given place_id
    url = f'https://maps.googleapis.com/maps/api/geocode/json?place_id={place_id}&key={API_KEY}'
    try:
      response = requests.get(url)
      response.raise_for_status()  # Raise an exception for 4xx/5xx errors

      # Get long and lat
      geo_data = response.json()["results"][0]["geometry"]["location"]
      self.lat = geo_data["lat"]
      self.lng = geo_data["lng"]

      # Get county
      address_components = response.json()["results"][0]["address_components"]
      for component in address_components:
        if len(component['types']) > 0 and component['types'][0] == 'administrative_area_level_2':
          self.county = component['long_name']
        if len(component['types']) > 0 and component['types'][0] == 'locality':
          self.town = component['long_name']
      
      # Get address
      self.address = response.json()["results"][0]["formatted_address"]

    except Exception as e:
      abort(500)
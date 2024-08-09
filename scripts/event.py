from app import db
from datetime import datetime
import requests
import os
import pytz

API_KEY = os.environ.get('API_KEY')

class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  created_date = db.Column(db.Date, nullable=False)
  created_time = db.Column(db.Time, nullable=False)
  venue_name = db.Column(db.String(50), nullable=False)
  band_name = db.Column(db.String(50), nullable=False)
  band_type = db.Column(db.String, nullable=False)
  tribute_band_name = db.Column(db.String, nullable=False)
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  event_date = db.Column(db.Date, nullable=False)
  start_time = db.Column(db.Time, nullable=False)
  end_time = db.Column(db.Time, nullable=True)
  address_id = db.Column(db.String, nullable=False)
  cover_charge = db.Column(db.Float, nullable=False)
  other_info = db.Column(db.String(250), nullable=True)
  facebook_handle = db.Column(db.String, nullable=True)
  instagram_handle = db.Column(db.String, nullable=True)
  website = db.Column(db.String, nullable=True)
  band_or_venue = db.Column(db.String, nullable=True)
  phone_number = db.Column(db.String, nullable=True)
  address_description = db.Column(db.String, nullable=False)
  event_id = db.Column(db.String, nullable=False)
  email_address = db.Column(db.String, nullable=False)
  
  def __init__(self, venue_name, band_name, band_type, tribute_band_name, genres, event_date, 
               start_time, end_time, address_id, cover_charge, other_info, facebook_handle,
               instagram_handle, website, band_or_venue, phone_number, address_description, event_id,
               email_address):
    self.venue_name = venue_name
    self.band_name = band_name
    self.band_type = band_type
    self.tribute_band_name = tribute_band_name
    self.genres = genres
    self.event_date = event_date
    self.start_time = start_time
    self.end_time = end_time
    self.address_id = address_id
    self.cover_charge = cover_charge
    self.other_info = other_info
    self.facebook_handle = facebook_handle
    self.instagram_handle = instagram_handle
    self.website = website
    self.band_or_venue = band_or_venue
    self.phone_number = phone_number
    self.address_description = address_description
    self.event_id = event_id
    self.email_address = email_address
    self.created_date = datetime.now(pytz.timezone("US/Eastern")).date().strftime("%Y-%m-%d")
    self.created_time = datetime.now(pytz.timezone("US/Eastern")).time().strftime("%H:%M:%S")

  def set_distance_data(self, origin_place_id):
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:{origin_place_id}&destinations=place_id:{self.address_id}&units=imperial&key={API_KEY}'

    try:
      response = requests.get(url)
      response.raise_for_status()  # Raise an exception for 4xx/5xx errors

      data = response.json()
      
      # Check if the response contains valid data
      if data['status'] == 'OK':
        self.distance_formatted = data['rows'][0]['elements'][0]['distance']['text']
        self.distance_value = data['rows'][0]['elements'][0]['distance']['value']
        self.address = data['destination_addresses'][0]
        return True
      else:
        print(f"Error: {data['status']}")
        print(data)
        return False

    except requests.exceptions.RequestException as e:
        print(f"Error fetching distance matrix: {e}")
        return False
    

  def get_all_details(self):
    # Create event_datetime_str
    event_date_str = self.event_date.strftime("%Y-%m-%d")
    event_time_str = self.start_time.strftime("%H:%M:%S")
    event_datetime_str = datetime.strptime(f'{event_date_str} {event_time_str}', 
                                           "%Y-%m-%d %H:%M:%S").isoformat()
    # Create created_datetime_str and created_datetime_formatted
    created_date_str = self.created_date.strftime("%Y-%m-%d")
    created_time_str = self.created_time.strftime("%H:%M:%S")
    created_datetime_str = datetime.strptime(f'{created_date_str} {created_time_str}', 
                                             "%Y-%m-%d %H:%M:%S").isoformat()
    created_datetime_formatted = datetime.strptime(f'{created_date_str} {created_time_str}', 
                                                   "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y at %#I:%M %p")

    return {
      "id": self.id,
      "venue_name": self.venue_name,
      "band_name": self.band_name,
      "band_type": self.band_type,
      "start_time_formatted": self.start_time.strftime("%#I:%M %p"),
      "end_time": None if self.end_time is None else self.end_time.strftime("%#I:%M %p"),
      "cover_charge": self.cover_charge,
      "date_formatted": self.event_date.strftime("%B %d, %Y"),
      "distance_formatted": self.distance_formatted if hasattr(self, "distance_formatted") else "",
      "address": self.address if hasattr(self, "address") else "",
      "genres": self.genres,
      "tribute_band_name": self.tribute_band_name,
      "other_info": self.other_info,
      "distance_value": self.distance_value if hasattr(self, "distance_value") else -1,
      "date_string": self.event_date.strftime("%Y-%m-%d"),
      "start_time_value": self.start_time.hour * 3600 + self.start_time.minute * 60,
      "facebook_handle": self.facebook_handle,
      "instagram_handle": self.instagram_handle,
      "website": self.website,
      "phone_number": self.phone_number,
      "band_or_venue": self.band_or_venue,
      "address_description": self.address_description,
      "address_id": self.address_id,
      "event_id": self.event_id,
      "email_address": self.email_address,
      "created_date_formatted": created_datetime_formatted,
      "created_datetime": created_datetime_str,
      "event_datetime": event_datetime_str,
    }
  
  def get_metadata(self):
    return {
      "id": self.id,
      "created_date": self.created_date.strftime("%Y-%m-%d"),
      "created_time": self.created_time.strftime("%H:%M:%S"),
      "event_id": self.event_id,
    }
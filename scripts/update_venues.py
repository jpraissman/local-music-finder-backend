from scripts.models.event import Event
from scripts.models.venue import Venue
from scripts.models.band import Band
from app import db

events: list[Event] = Event.query.all()
venues: list[Venue] = Venue.query.all()
bands: list[Band] = Band.query.all()

count = 0
for event in events:
  count += 1
  if event.band_or_venue == "Venue":
    for venue in venues:
      if event.venue_id == venue.id:
        venue.phone_number = event.phone_number if event.phone_number != "" else venue.phone_number
        venue.facebook_url = event.facebook_handle if event.facebook_handle != "" else venue.facebook_url
        venue.instagram_url = event.instagram_handle if event.instagram_handle != "" else venue.instagram_url
        venue.website_url = event.website if event.website != "" else venue.website_url
  else:
    for band in bands:
      if event.band_id == band.id:
        band.facebook_url = event.facebook_handle if event.facebook_handle != "" else band.facebook_url
        band.instagram_url = event.instagram_handle if event.instagram_handle != "" else band.instagram_url
        band.website_url = event.website if event.website != "" else band.website_url
  if count % 100 == 0:
    print(f"Processed {count} events...")
db.session.commit()
  



from scripts.models.band import Band
from app import db

bands: list[Band] = Band.query.all()

for band in bands:
  band.youtube_ids = []
  db.session.add(band)
  db.session.commit()

print("Done")

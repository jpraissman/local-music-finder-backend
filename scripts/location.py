from app import db

class Location(db.Model):
  __tablename__ = "location"
  id = db.Column(db.Integer, primary_key=True)
  location = db.Column(db.String, nullable=False)
  event_distances = db.relationship('EventDistance', backref='location')

  def __init__(self, location:str):
    self.location = location
from app import db
from datetime import datetime

class Visit(db.Model):
  __tablename__ = "visit"
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  path = db.Column(db.String, nullable=False)
  from_where = db.Column(db.String, nullable=False)
  user_id = db.Column(db.String, nullable=False)

  def __init__(self, path: str, from_where: str, user_id: str):
    self.path = path
    self.from_where = from_where
    self.user_id = user_id
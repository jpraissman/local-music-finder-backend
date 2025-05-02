from flask import Blueprint, request, Response
import csv, io
from typing import List
from sqlalchemy import desc
from app import db
from scripts.models.visit import Visit

visit_bp = Blueprint('visit', __name__)

# Create a Visit
@visit_bp.route('/visit', methods = ['POST'])
def create_visit():
  page = request.json['page']
  from_where = request.json['from']
  user_id = request.json['user']

  visit = Visit(page, from_where, user_id)
  db.session.add(visit)
  db.session.commit()

  return "Visit Created"

# Get a CSV file of all the visits
@visit_bp.route('/all-visits', methods= ['GET'])
def get_all_visits():
  # Step 1: Create an in-memory string buffer
  csv_buffer = io.StringIO()

  # Step 2: Use the csv writer to write to the buffer
  writer = csv.writer(csv_buffer)
  writer.writerow(['Visit Date', 'Page', 'From', 'User'])  # CSV header

  visits: List[Visit] = Visit.query.order_by(desc(Visit.created_at)).all()
  for visit in visits:
    writer.writerow([visit.created_at, visit.page, visit.from_where, visit.user_id])

  # Step 3: Set the buffer's position to the start (so it can be read)
  csv_buffer.seek(0)

  # Step 4: Create a Flask Response, passing the CSV data as content
  response = Response(csv_buffer.getvalue(), mimetype='text/csv')

  # Step 5: Set the content-disposition header to prompt a download
  response.headers['Content-Disposition'] = 'attachment; filename=visits.csv'

  return response
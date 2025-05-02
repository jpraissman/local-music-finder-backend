from flask import Blueprint, Response
from typing import List
from sqlalchemy import desc
from scripts.models.query import Query
import io, csv

query_bp = Blueprint('query', __name__)

# Get a CSV file of all the queries
@query_bp.route('/all-queries', methods= ['GET'])
def get_all_queries():
  # Step 1: Create an in-memory string buffer
  csv_buffer = io.StringIO()

  # Step 2: Use the csv writer to write to the buffer
  writer = csv.writer(csv_buffer)
  writer.writerow(['Search Date', 'Date Range', 'Location', 'Distance',
                   'Genres', 'Band Types', 'From', 'Id'])  # CSV header

  queries: List[Query] = Query.query.order_by(desc(Query.created_at)).all()
  for query in queries:
    writer.writerow([query.created_at, query.time_range, query.location,
                     query.distance, query.genres, query.band_types, query.from_where, query.id])

  # Step 3: Set the buffer's position to the start (so it can be read)
  csv_buffer.seek(0)

  # Step 4: Create a Flask Response, passing the CSV data as content
  response = Response(csv_buffer.getvalue(), mimetype='text/csv')

  # Step 5: Set the content-disposition header to prompt a download
  response.headers['Content-Disposition'] = 'attachment; filename=searches.csv'

  return response
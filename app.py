# Imports
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import time
import os, json, time, traceback
import scripts.send_emails as EmailSender
from flask_executor import Executor
from flask_limiter import Limiter
from flask_migrate import Migrate

# Important server stuff
app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url.startswith("postgres:"):
  database_url = database_url.replace("postgres:", "postgresql:", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
executor = Executor(app)
limiter = Limiter(app=app, key_func=lambda: "global", default_limits=["100 per minute"])

# Get API Keys
API_KEY = os.environ.get('API_KEY')
ADMIN_KEY = os.environ.get('ADMIN_KEY')

# Must be imported after to avoid circular import
from api.event import event_bp
from api.query import query_bp
from api.visit import visit_bp

app.register_blueprint(event_bp)
app.register_blueprint(query_bp)
app.register_blueprint(visit_bp)

# Import database models so they are seen
from scripts.models.band import Band
from scripts.models.event import Event
from scripts.models.query import Query
from scripts.models.venue import Venue
from scripts.models.visit import Visit

# Used to make helper send rate limit emails
class RateLimitEmailHelper:
  email_sent = False

# Custom 404 error handler
@app.errorhandler(404)
def not_found(error):
    # Return an empty response
    return Response(status=200)

@app.errorhandler(Exception)
def handle_exception(e):
  print("Handling Error")

  tb = traceback.format_exc()

  request_info = {
    "method": request.method,
    "url": request.url,
    "headers": dict(request.headers),
    "body": request.get_data(as_text=True)
  }

  response = {
    "error": {
      "type": type(e).__name__,
      "message": str(e),
      "traceback": tb
    },
    "request": request_info,
    "path": request.path
  }

  EmailSender.send_error_occurred_email(json.dumps(response, indent=8))
  return jsonify(response), 500

# Handles rate limit errors by sending an email alerting that a rate limit has been hit
@app.errorhandler(429)
def handle_rate_limit_exception(e):
  print("Handling Rate Limit Error")
  if not RateLimitEmailHelper.email_sent:
    EmailSender.send_error_occurred_email("The API limit was hit: Too many requests in the last minute have been made (Over 100 requests).")
    RateLimitEmailHelper.email_sent = True
    executor.submit(reset_rate_limit_email)
    print("Sent email and submitted reset request")
  
  return jsonify("Too many requests have been made in the last minute"), 429

# Resets rate limit email so emails can be sent again when the application hits a rate limit.
def reset_rate_limit_email():
  time.sleep(1200)
  RateLimitEmailHelper.email_sent = False
  print("Reset rate limit email")

if __name__ == '__main__':
  app.run()
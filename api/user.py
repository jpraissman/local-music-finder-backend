from flask import Blueprint, jsonify, request
from scripts.models.user import User
from scripts.models.session import Session
from app import db
from scripts.user_helpers import get_user, is_bot
from functools import wraps
from app import ADMIN_KEY
from collections.abc import Callable
from datetime import datetime, time
from scripts.user_helpers import get_device_type, format_referer
import math

user_bp = Blueprint('user', __name__)

# This is a higher order function that confirms the request has the correct admin key to access the resource.
# If not, this function throws an Unauthorized error.
def validate_admin_key(f: Callable) -> Callable:
  @wraps(f)
  def decorated_function(*args, **kwargs):
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
      return jsonify({'error': 'You must be an admin to access this.'}), 401
    return f(*args, **kwargs)
  return decorated_function

@user_bp.route('/users', methods=['GET'])
@validate_admin_key
def get_new_users():
  from_date = request.args.get('from_date')
  to_date = request.args.get('to_date')
  to_date = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), time(hour=23, minute=59, second=59))
  include_admins = request.args.get('include_admins', 'false')
  filter_out_zero_duration = request.args.get('filter_out_zero_duration', 'true')

  all_sessions: list[Session] = Session.query.filter(Session.start_time >= from_date,
                                                     Session.start_time <= to_date).all()
  
  user_results = {}
  for session in all_sessions:
    user_id = session.user_id
    if (user_id not in user_results 
        and (include_admins == 'true' or not session.user.is_admin)
        and (filter_out_zero_duration == 'false' or (session.end_time - session.start_time).total_seconds() > 0)):
      user_results[user_id] = {
        'user_id': user_id,
        'duration': math.ceil((session.end_time - session.start_time).total_seconds() / 60),
        'device': get_device_type(session.user_agent),
        'referer': format_referer(session.referer),
        'videos_clicked': len(session.clicked_videos),
        'events_viewed': len(session.viewed_events),
        'type': 'new' if session.user.sessions[0].id == session.id else 'returning',
        'pages_visited': len(session.activities),
      }
    elif ((include_admins == 'true' or not session.user.is_admin)
          and (filter_out_zero_duration == 'false' or (session.end_time - session.start_time).total_seconds() > 0)):
      user_results[user_id]['duration'] += round((session.end_time - session.start_time).total_seconds() / 60) + 1
      user_results[user_id]['videos_clicked'] += len(session.clicked_videos)
      user_results[user_id]['events_viewed'] += len(session.viewed_events)
      user_results[user_id]['pages_visited'] += len(session.activities)
      if session.user.sessions[0].id == session.id:
        user_results[user_id]['type'] = 'new'

  # Get totals
  totals = {
    "total_users": len(user_results),
    "total_new_users": sum(1 for user in user_results.values() if user['type'] == 'new'),
    "total_returning_users": sum(1 for user in user_results.values() if user['type'] == 'returning'),
    "total_mobile_users": sum(1 for user in user_results.values() if user['device'] == 'mobile'),
    "total_tablet_users": sum(1 for user in user_results.values() if user['device'] == 'tablet'),
    "total_computer_users": sum(1 for user in user_results.values() if user['device'] == 'computer'),
    "total_facebook_referers": sum(1 for user in user_results.values() if user['referer'] == 'facebook'),
    "total_reddit_referers": sum(1 for user in user_results.values() if user['referer'] == 'reddit'),
    "total_google_referers": sum(1 for user in user_results.values() if user['referer'] == 'google'),
    "total_patch_referers": sum(1 for user in user_results.values() if user['referer'] == 'patch'),
    "total_unknown_referers": sum(1 for user in user_results.values() if user['referer'] == 'unknown'),
    "total_videos_clicked": sum(user['videos_clicked'] for user in user_results.values()),
    "total_events_viewed": sum(user['events_viewed'] for user in user_results.values()),
    "total_pages_visited": sum(user['pages_visited'] for user in user_results.values()),
    "total_duration": sum(user['duration'] for user in user_results.values())
  }

  return jsonify({"users": user_results, "totals": totals}), 200


@user_bp.route('/video-clicked', methods=['POST'])
def add_video_click():
  # Check if the request came from a bot
  user_agent = request.json['user_agent']
  user_is_bot = is_bot(user_agent)
  if not user_is_bot:
    # Get parameters
    user_id = request.json['user_id']
    event_id = request.json['event_id']

    user: User = get_user(user_id, db)
    user.add_video_click(event_id)
    db.session.commit()

  return jsonify({"status": "success"}), 200

@user_bp.route('/activity', methods=['POST'])
def add_activity():
  user_agent = request.json['user_agent']
  page = request.json['page']
  ip = request.json['ip']
  referer = request.json['referer']
  user_is_bot = is_bot(user_agent, is_query=False, page=page, ip=ip, referer=referer, track_activity=True)

  if not user_is_bot:
    user_id = request.json['user_id']
    user: User = get_user(user_id, db)
    user.add_activity(page, user_agent, ip, referer)
    db.session.commit()

  return jsonify({"status": "success"}), 200




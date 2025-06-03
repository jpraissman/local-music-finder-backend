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

  all_sessions: list[Session] = Session.query.filter(Session.start_time >= from_date,
                                                     Session.start_time <= to_date).all()
  
  user_results = {}
  for session in all_sessions:
    user_id = session.user_id
    if user_id not in user_results:
      user_results[user_id] = {
        'user_id': user_id,
        'duration': round((session.end_time - session.start_time).total_seconds() / 60) + 1,
        'device': get_device_type(session.user_agent),
        'referer': format_referer(session.referer),
        'videos_clicked': len(session.clicked_videos),
        'events_viewed': len(session.viewed_events),
        'type': 'new' if session.user.sessions[-1].id == session.id else 'returning',
      }
    else:
      user_results[user_id]['duration'] += round((session.end_time - session.start_time).total_seconds() / 60) + 1
      user_results[user_id]['videos_clicked'] += len(session.clicked_videos)
      user_results[user_id]['events_viewed'] += len(session.viewed_events)

  return jsonify({"users": user_results}), 200


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




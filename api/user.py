from flask import Blueprint, jsonify, request
from scripts.models.user import User
from app import db
from scripts.user_helpers import get_user, is_bot
from scripts.models.bot_activity import BotActivity

user_bp = Blueprint('user', __name__)

@user_bp.route('/video-clicked', methods=['POST'])
def add_video_click():
  # Check if the request came from a bot
  user_agent = request.json['user_agent']
  user_is_bot = is_bot(user_agent)
  if user_is_bot:
    pass
  else:
    # Get parameters
    user_id = request.json['user_id']
    event_id = request.json['event_id']

    user: User = get_user(user_id, db)
    user.add_video_click(event_id)
    db.session.commit()

  return jsonify({"status": "success"}), 200

@user_bp.route('/activity', methods=['POST'])
def add_activity():
  # Check if the request came from a bot
  user_agent = request.json['user_agent']
  user_is_bot = is_bot(user_agent)
  if user_is_bot:
    page = request.json['page']
    ip = request.json['ip']
    referer = request.json['referer']

    new_bot_activity = BotActivity(page, user_agent, ip, referer)
    db.session.add(new_bot_activity)
    db.session.commit()
  else:
    # Get parameters
    user_id = request.json['user_id']
    page = request.json['page']
    ip = request.json['ip']
    referer = request.json['referer']

    user: User = get_user(user_id, db)
    user.add_activity(page, user_agent, ip, referer)
    db.session.commit()

  return jsonify({"status": "success"}), 200




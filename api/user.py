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




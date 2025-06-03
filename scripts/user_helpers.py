from user_agents import parse
from scripts.models.user import User
from app import db
from scripts.models.bot_activity import BotActivity

other_bot_keywords = ["vercel-screenshot", "Google-InspectionTool", "GoogleOther"]

def is_bot(user_agent_str: str, is_query: bool = False, page: str = None, 
           ip: str = None, referer: str = None, track_activity: bool = False):
  user_agent = parse(user_agent_str)
  user_is_bot = user_agent.is_bot or any(keyword in user_agent_str for keyword in other_bot_keywords)

  if user_is_bot and track_activity:
    track_bot_activity(user_agent_str, is_query, page, ip, referer)

  return user_is_bot

def track_bot_activity(user_agent: str, is_query: bool, page: str, ip: str, referer: str):
  new_bot_activity = BotActivity(page, user_agent, ip, referer, is_query)
  db.session.add(new_bot_activity)
  db.session.commit()

def format_referer(referer: str) -> str:
  if not referer:
    return "unknown"
  if "facebook" in referer:
    return "facebook"
  if "reddit" in referer:
    return "reddit"
  if "google" in referer:
    return "google"
  if "patch" in referer:
    return "patch"
  return "unknown"

def get_device_type(user_agent_str: str) -> str:
  if not user_agent_str:
    return "unknown"
  
  user_agent = parse(user_agent_str)
  if user_agent.is_mobile:
    return "mobile"
  elif user_agent.is_tablet:
    return "tablet"
  elif user_agent.is_pc:
    return "computer"
  else:
    return "unknown"

def get_user(user_id: str, db):
  user = User.query.filter_by(id=user_id).first()
  if not user:
    user = User(user_id)
    db.session.add(user)
  return user
from user_agents import parse
from scripts.models.user import User

def is_bot(user_agent_str: str):
  user_agent = parse(user_agent_str)
  return user_agent.is_bot

def get_user(user_id: str, db):
  user = User.query.filter_by(id=user_id).first()
  if not user:
    user = User(user_id)
    db.session.add(user)
  return user
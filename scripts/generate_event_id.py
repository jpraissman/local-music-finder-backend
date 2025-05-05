from scripts.models.event import Event
import random, string

# Generates a random 8 character event id
def generate_event_id():
  # Generate random id
  unique_id_found = False
  while not unique_id_found: 
    characters = string.ascii_letters + string.digits
    new_event_id = ''.join(random.choice(characters) for _ in range(8))
    try:
      Event.query.filter_by(event_id=new_event_id).one()
      unique_id_found = False
    except:
      unique_id_found = True
  return new_event_id
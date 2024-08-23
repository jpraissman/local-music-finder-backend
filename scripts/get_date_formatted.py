from datetime import datetime, timedelta
import pytz

def get_date_formatted(date):
  et = pytz.timezone("US/Eastern")
  today = datetime.now(et).date()

  if (today == date):
    return "Today"
  elif (today + timedelta(days=1) == date):
    return "Tomorrow"
  else:
    return date.strftime("%A, %B %d")


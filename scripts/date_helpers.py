from datetime import datetime
import pytz

def get_eastern_datetime_now_str():
  return datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M:%S")

def get_eastern_datetime_now():
  return datetime.now(pytz.timezone("US/Eastern"))

def convert_to_eastern(dt):
  eastern = pytz.timezone("US/Eastern")
  if dt.tzinfo is None:
    return eastern.localize(dt)
  else:
    return dt.astimezone(eastern)
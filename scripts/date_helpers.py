from datetime import datetime
import pytz

def get_eastern_datetime_now_str():
  return datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M:%S")
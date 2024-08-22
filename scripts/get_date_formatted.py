from datetime import datetime, timedelta
import pytz

def get_date_formatted(date):
  et = pytz.timezone("US/Eastern")
  seven_days_away = datetime.now(et).date() + timedelta(days=7)

  if date < seven_days_away:
    return date.strftime("%A")
  else:
    return date.strftime("%B %d")


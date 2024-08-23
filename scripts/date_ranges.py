from datetime import datetime, timedelta
import pytz

def get_date_range(date_range):
  et = pytz.timezone("US/Eastern")
  today = datetime.now(et).date()

  if date_range == "Today":
    return today_range(today)
  elif date_range == "Tomorrow":
    return tomorrow(today)
  elif date_range == "This Weekend (Fri-Sun)":
    return this_weekend(today)
  elif date_range == "Next Weekend (Fri-Sun)":
    return next_weekend(today)
  elif date_range == "This Week (Mon-Sun)":
    return this_week(today)
  elif date_range == "Next Week (Mon-Sun)":
    return next_week(today)
  elif date_range == "Next 30 Days":
    return next_30_days(today)
  elif date_range == "Next 60 Days":
    return next_60_days(today)

# Returns the start and end date for this weekend (Fri-Sun)
def this_weekend(today):
  days_until_friday = 4 - today.weekday()
  days_until_saturday = 5 - today.weekday()
  days_until_sunday = 6 - today.weekday()

  days_until_start_date = days_until_friday
  if days_until_friday < 0:
    days_until_start_date = days_until_saturday
  if days_until_saturday < 0:
    days_until_start_date = days_until_sunday

  return (today + timedelta(days=days_until_start_date), today + timedelta(days=days_until_sunday))

# Returns the start and end date for next weekend (Fri-Sun)
def next_weekend(today):
  days_until_friday = 4 - today.weekday() + 7
  days_until_sunday = 6 - today.weekday() + 7

  return (today + timedelta(days=days_until_friday), today + timedelta(days=days_until_sunday))

# Returns the start and end date for this week (Mon-Sun)
def this_week(today):
  days_until_sunday = 6 - today.weekday()

  day = 0
  days_until_start_date = day - today.weekday()
  while (days_until_start_date < 0):
    day += 1
    days_until_start_date = day - today.weekday()

  return (today + timedelta(days=days_until_start_date), today + timedelta(days=days_until_sunday))

# Returns the start and end date for next week (Mon-Sun)
def next_week(today):
  days_until_monday = 0 - today.weekday() + 7
  days_until_sunday = 6 - today.weekday() + 7

  return (today + timedelta(days=days_until_monday), today + timedelta(days=days_until_sunday))

# Returns the start and end date for the next 30 days
def next_30_days(today):
  return (today, today + timedelta(days=30))

# Returns the start and end date for the next 60 days
def next_60_days(today):
  return (today, today + timedelta(days=60))

# Returns the start and end date for today
def today_range(today):
  return (today, today)

# Returns the start and end date for tomorrow
def tomorrow(today):
  return (today + timedelta(days=1), today + timedelta(days=1))
from datetime import datetime
import pytz

et = pytz.timezone("US/Eastern")
today = datetime.now(et)

print(today.strftime("%B %d, %Y at %#I:%M %p"))
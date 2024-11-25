from app import db

class EventDistance(db.Model):
  __tablename__ = "event_distance"
  id = db.Column(db.Integer, primary_key=True)
  event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
  location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
  distance = db.Column(db.Integer, nullable=False)

  def __init__(self, location_id:int, event_id:int):
    self.location_id = location_id
    self.event_id = event_id
    self.distance = 1000

    # # Calculate the distance
    # url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={location}&destinations={deve}&units=imperial&key={API_KEY}'
    # response = requests.get(url)
    # response.raise_for_status()  # Raise an exception for 4xx/5xx errors

    # data = response.json()
    
    # # Check if the response contains valid data
    # if data['status'] == 'OK':
    #   destination_addresses = data["destination_addresses"]
    #   elements = data['rows'][0]['elements']
    #   for index, element in enumerate(elements):
    #     distance_formatted = element['distance']['text']
    #     distance_value = element['distance']['value']
    #     new_address = destination_addresses[index]
    #     events[index].set_distance_data(distance_formatted, distance_value, new_address)
    #     if distance_value <= max_distance:
    #       returned_events.append(events[index].get_all_details(False, False))
    # else:
    #   print(f"Error: {data['status']}")
    #   # print(data)
    #   # return [False, origin, self.address, data]
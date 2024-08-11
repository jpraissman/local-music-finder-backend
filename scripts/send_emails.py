from googleapiclient.discovery import build
import base64
from email.message import EmailMessage
from scripts.get_email_creds import get_email_creds
import os

def send_event_email(event):
  creds = get_email_creds()

  try:
    if creds is None:
      raise ValueError("Given creds were invalid")
    
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()
    
    event_edit_link = os.environ.get('WEBSITE_URL') + "edit"
    body = f'<p>Thanks for creating an event with The Local Music Finder! Your event has been posted and is available for all users to see.</p><p>To <strong>edit</strong> or <strong>delete</strong> your event, <a href={event_edit_link}>click here</a> and paste in your Event ID: <strong>{event.event_id}</strong>.</p><p><span style="text-decoration: underline;">Your Event Details:</span><br /><em>Venue Name: </em>{event.venue_name}<br /> <em>Venue Address: </em>{event.address_description}<br /><em>Band Name:</em>&nbsp;{event.band_name}<br /><em>Band Type:</em> {event.band_type}<br /><em>Band Genres:</em> {", ".join(event.genres)}<br /><em>Event Date: </em>{event.event_date.strftime("%B %d, %Y")}<br /> <em>Start Time: </em>{event.start_time.strftime("%I:%M %p")}</p><br /><p>Sincerely,<br />The Local Music Finder</p>' 
    message.set_content(body, 'html')

    message["To"] = event.email_address
    message["From"] = os.environ.get('INFO_EMAIL_ADDRESS')
    message["Subject"] = f"Your event on {event.event_date.strftime("%B %d")} has been created!"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    service.users().messages().send(userId="me", body=create_message).execute()

    return True
  except Exception as e:
    print(f"An email error occurred: {e}")

    return False
  
def send_admin_event_email(event):
  creds = get_email_creds()

  try:
    if creds is None:
      raise ValueError("Given creds were invalid")
    
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    body = f'<p>An event has been created.</p><p><span style="text-decoration: underline;">Event Details:</span><br /><strong><em>Venue Name: </em></strong>{event.venue_name}<br /> <strong><em>Venue Address: </em></strong>{event.address_description}<br /><strong><em>Band Name:</em></strong>&nbsp;{event.band_name}<br /><strong><em>Band Type:</em></strong> {event.band_type}<br /><strong><em>Tribute Band Name:</em></strong> {event.tribute_band_name}<br /><strong><em>Band Genres:</em></strong> {", ".join(event.genres)}<br /><strong><em>Event Date: </em></strong>{event.event_date.strftime("%B %d, %Y")}<br /> <strong><em>Start Time: </em></strong>{event.start_time.strftime("%I:%M %p")}<br /><strong><em>Cover Charge:</em></strong> {event.cover_charge}<br /><strong><em>Other Info:</em></strong> {event.other_info}<br /><strong><em>Facebook Handle:</em></strong> {event.facebook_handle}<br /><strong><em>Instagram Handle:</em></strong> {event.instagram_handle}<br /><strong><em>Website:</em></strong> {event.website}<br /><strong><em>Venue Phone Number:</em></strong> {event.phone_number}<br /><strong><em>Email Address:</em></strong> {event.email_address}</p>'
    message.set_content(body, 'html')

    message["To"] = os.environ.get('INFO_EMAIL_ADDRESS')
    message["From"] = os.environ.get('INFO_EMAIL_ADDRESS')
    message["Subject"] = f"An event at {event.venue_name} has been created"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    service.users().messages().send(userId="me", body=create_message).execute()

    return True
  except Exception as e:
    print(f"An email error occurred: {e}")

    return False


def send_duplicate_event_email(events):
  creds = get_email_creds()

  try:
    if creds is None:
      raise ValueError("Given creds were invalid")
    
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    body = f"<p>There are {len(events)} potential duplicate events on <strong>{events[0].event_date.strftime("%B %d, %Y")}</strong></p><br />"
    count = 1
    for event in events:
      body += f"<p>Event {count}: At <strong>{event.venue_name}</strong> with the address <strong>{event.address_description}</strong>.</p>"
      count += 1

    message.set_content(body, 'html')

    message["To"] = os.environ.get('INFO_EMAIL_ADDRESS')
    message["From"] = os.environ.get('INFO_EMAIL_ADDRESS')
    message["Subject"] = "There are potential duplicate events"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    service.users().messages().send(userId="me", body=create_message).execute()

    return True
  except Exception as e:
    print(f"An email error occurred: {e}")

    return False

def send_weekly_event_notification(user, events):
  creds = get_email_creds()

  try:
    if creds is None:
      raise ValueError("Given creds were invalid")
    
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    temp_date = "All Future Dates"

    events_url = f'http://localhost:5173/find?date={temp_date}&distance={user.max_distance}&genres={"/".join(user.genres)}&bands={"/".join(user.band_types)}&address={user.address_description}&placeId={user.address_id}'

    body = f'<p>{events_url}</p>'
    message.set_content(body, 'html')

    message["To"] = user.email_address
    message["From"] = os.environ.get('INFO_EMAIL_ADDRESS')
    message["Subject"] = f"There are {len(events)} live music events for you this week!"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    service.users().messages().send(userId="me", body=create_message).execute()

    return True
  except Exception as e:
    print(f"An email error occurred: {e}")

    return False
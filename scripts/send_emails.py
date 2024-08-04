from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
from scripts.get_email_creds import get_email_creds
import os

def send_event_email(event):
  creds = get_email_creds()

  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    body = f'<p style="text-align: left;">Thanks for creating an event with The Local Music Finder! Your event has been posted and is available for all users to see.</p><p style="text-align: left;">To <strong>edit</strong> or <strong>delete</strong> your event, go to <a href="http://localhost:5173/edit">this link</a> and paste in your Event ID: <strong>{event.event_id}</strong>.</p><p style="text-align: left;">&nbsp;</p><p style="text-align: left;"><img src="./logo2.png" alt="The Local Music Finder" width="100" height="100" /></p>'
    message.set_content(body, 'html')

    message["To"] = event.email_address
    message["From"] = os.environ.get('EMAIL_SENDER_ADDRESS')
    message["Subject"] = f"Your Event At {event.venue_name} Has Been Created!"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message


def send_duplicate_event_email(events):
  creds = get_email_creds()

  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    body = ""
    count = 1
    for event in events:
      body += f"<p>Event ID {count}: {event.event_id}</p>\n"
      count += 1

    message.set_content(body, 'html')

    message["To"] = os.environ.get('EMAIL_SENDER_ADDRESS')
    message["From"] = os.environ.get('EMAIL_SENDER_ADDRESS')
    message["Subject"] = "There are potential duplicate events"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message
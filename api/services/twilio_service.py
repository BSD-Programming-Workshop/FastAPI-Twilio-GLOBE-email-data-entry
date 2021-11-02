from decouple import config
from twilio.rest import Client

from api.models import Measurement, Observer

DOMAIN = config("DOMAIN")
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
TWILIO_SMS_NUMBER = config("TWILIO_SMS_NUMBER")


def send_webpage_url(observer: Observer, measurement: Measurement):
    client = Client(username=TWILIO_ACCOUNT_SID, password=TWILIO_AUTH_TOKEN)

    from_number = TWILIO_SMS_NUMBER
    to_number = observer.phone
    # Note: Message must conform to a couple of template options:
    # see: https://www.twilio.com/console/sms/whatsapp/sandbox
    message_body = f"Your measurement graphic code is available at {DOMAIN}/measurement_graphic/{measurement.id}"

    resp = client.messages.create(to=to_number, from_=from_number, body=message_body)
    if resp.error_message:
        raise Exception(f"Cannot send twilio message: {resp.error_message}.")

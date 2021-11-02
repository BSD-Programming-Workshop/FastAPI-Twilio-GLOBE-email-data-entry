from typing import Optional

import python_http_client
from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Email,
    Mail,
    PlainTextContent,
    SendGridException,
    Subject,
    To,
)

from api.models import Measurement, Observer

SENDGRID_SECRET_KEY = config("SENDGRID_SECRET_KEY")
SENDGRID_VERIFIED_EMAIL = config("SENDGRID_VERIFIED_EMAIL")


def compute_celsius_temperature(scale, temp):
    ONE_DECIMAL = ".1f"
    if scale.startswith("f"):
        compute = (temp - 32) * 0.5556
        return f"{compute:{ONE_DECIMAL}}"

    return f"{temp:{ONE_DECIMAL}}"


def format_datetime_for_globe(datetime):
    return datetime.strftime("%Y%m%d%I%M")


def send_email_data_entry(observer: Observer, measurement: Measurement):
    temperature_in_celsius = compute_celsius_temperature(
        measurement.temperaturescale, measurement.temperature
    )
    measurement_datetime = format_datetime_for_globe(measurement.date_time)
    sg = SendGridAPIClient(SENDGRID_SECRET_KEY)
    from_email = Email(SENDGRID_VERIFIED_EMAIL)
    to_email = To("globedata@ucar.edu")
    subject = Subject("DATA")
    content = PlainTextContent(
        "//AA\nATMNN "
        f"ORG_ID:{measurement.organizationid} SITE_ID:{measurement.siteid} {measurement_datetime} {temperature_in_celsius}\n//ZZ"
    )
    message = Mail(from_email, to_email, subject, content)

    try:
        response: python_http_client.client.Response = sg.send(message)
        print(
            f"Sent email successfully: GLOBE EMDE sent with temperature reading of {temperature_in_celsius} Celsius"
        )

    except SendGridException as e:
        print(e.message)

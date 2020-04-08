import uuid
import datetime
import os
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.db import models
import phonenumbers
from twilio.rest import Client

# Create your models here.


TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
PHONE_NUMBER = os.environ["PHONE_NUMBER"]


def generate_random_code():
    return str(uuid.uuid4())


class User(AbstractUser):
    is_coordinator = models.BooleanField(default=False)


class Invite(models.Model):
    code = models.CharField(
        primary_key=True, max_length=36, default=generate_random_code
    )
    used = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("invite-detail", args=[self.code])


class Call(models.Model):
    twilio_sid = models.CharField(max_length=40)
    handled_at = models.DateTimeField(null=True, default=None)
    delivered_at = models.DateTimeField(null=True, default=None)
    comment = models.CharField(max_length=1000, null=True, blank=True, default=None)
    recording_url = models.CharField(
        max_length=500, null=True, blank=True, default=None
    )
    duration = models.IntegerField(default=0)
    number: str
    timestamp: datetime.datetime

    @property
    def handled(self):
        return self.handled_at is not None

    @property
    def delivered(self):
        return self.delivered_at is not None


# TODO: cache these in our database
def list_calls() -> List[Call]:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    twilio_calls = client.calls.list(to=PHONE_NUMBER, limit=1000)
    db_calls = {c.twilio_sid: c for c in Call.objects.all()}
    calls: List[Call] = []
    for tc in twilio_calls:
        c = twilio_call_to_call(db_calls, tc)
        calls.append(c)
    return calls


def twilio_call_to_call(db_calls: Dict[str, Call], tc) -> Call:
    sid = tc.sid
    call = db_calls.get(sid)
    timestamp = tc.date_created
    number = format_number(tc.from_)

    if not call:
        recording_url, duration = get_recording(tc)
        call = Call(
            twilio_sid=sid,
            duration=duration,
            recording_url=recording_url,
            handled_at=None,
            delivered_at=None,
            comment=None,
        )
        call.save()

    call.timestamp = timestamp
    call.number = number

    return call


def format_number(raw: str) -> str:
    number = phonenumbers.parse(raw)
    if number.country_code == 46:
        fmt = phonenumbers.PhoneNumberFormat.NATIONAL
    else:
        fmt = phonenumbers.PhoneNumberFormat.INTERNATIONAL
    return phonenumbers.format_number(number, fmt)


def get_recording(tc) -> Tuple[Optional[str], int]:
    recs = tc.recordings.list()
    if not recs:
        return None, 0
    rec = recs[0]
    duration = int(rec.duration)
    if duration <= 0:
        return None, 0
    uri = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Recordings/{rec.sid}.mp3"
    return uri, duration

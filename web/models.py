from collections import defaultdict
import uuid
import datetime
import os
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import pytz
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
    elif not call.duration and timestamp > one_week_ago():
        print(timestamp)
        recording_url, duration = get_recording(tc)
        call.recording_url = recording_url
        call.duration = duration
        call.save()

    call.timestamp = timestamp
    call.number = number

    return call


def one_week_ago():
    tz = pytz.timezone("Europe/Stockholm")
    return (datetime.datetime.today() - datetime.timedelta(days=7)).replace(tzinfo=tz)


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
    recs.sort(key=lambda r: -int(r.duration))
    rec = recs[0]
    duration = int(rec.duration)
    if duration <= 0:
        return None, 0
    uri = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Recordings/{rec.sid}.mp3"
    return uri, duration


def calls_per_week():
    calls = list_calls()
    per_week = group_calls_per_week(calls)
    table = []
    for day, calls in per_week.items():
        all_calls = len(calls)
        calls_with_fb = len(
            [c for c in calls if c.comment and "facebook.com" in c.comment]
        )
        table.append(
            {
                "day": day.strftime("%Y-%m-%d"),
                "all_calls": all_calls,
                "calls_with_fb": calls_with_fb,
            }
        )
    print(table)
    return sorted(table, key=lambda r: r["day"], reverse=True)


def group_calls_per_week(calls: List[Call]):
    tz = pytz.timezone("Europe/Stockholm")
    per_week: Dict[datetime.datetime, List[Call]] = {}

    start_date = "2020-03-16"
    start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=tz)
    end_time = datetime.datetime.now().replace(tzinfo=tz)
    t = start_time
    while t < end_time:
        week_end = t + datetime.timedelta(days=7)
        per_week[t] = []
        for c in calls:
            if c.timestamp >= t and c.timestamp < week_end:
                per_week[t].append(c)
        t = week_end

    return per_week

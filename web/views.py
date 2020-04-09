from datetime import datetime
import os
import pytz
from django.forms.models import model_to_dict
from django.utils.timezone import activate as activate_timezone
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from web import models


def coordinator_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_coordinator or request.user.is_superuser:
            return fn(request, *args, **kwargs)

        print(request.session.__dict__)
        if "invite_code" not in request.session:
            return HttpResponseForbidden()

        pk = request.session["invite_code"]
        invite = get_object_or_404(models.Invite, pk=pk, used=False)
        request.user.is_coordinator = True
        request.user.save()
        invite.used = True
        invite.user = request.user
        invite.save()
        return fn(request, *args, **kwargs)

    return wrapper


def fb_user(user):
    return user.social_auth.get(provider="facebook")


def index(request):
    return render(request, "index.html")


def login(request):
    return render(request, "login.html")


def invite_detail(request, pk):
    invite = get_object_or_404(models.Invite, pk=pk, used=False)
    request.session["invite_code"] = invite.code
    return redirect(settings.LOGIN_URL)


@login_required
@coordinator_required
def manage_calls(request):
    activate_timezone(pytz.timezone("Europe/Stockholm"))
    calls = models.list_calls()
    volunteer_sheet = os.environ["VOLUNTEER_SHEET"]
    return render(
        request, "calls.html", {"calls": calls, "volunteer_sheet": volunteer_sheet}
    )


@login_required
@coordinator_required
def call_posted(request):
    posted = request.POST["posted"]
    sid = request.POST["sid"]
    call = models.Call.objects.get(twilio_sid=sid)
    if posted == "true":
        call.handled_at = datetime.now()
        call.save()
        return HttpResponse("Saved")
    else:
        call.handled_at = None
        call.save()
        return HttpResponse("Deleted")


@login_required
@coordinator_required
def call_delivered(request):
    delivered = request.POST["delivered"]
    sid = request.POST["sid"]
    call = models.Call.objects.get(twilio_sid=sid)
    if delivered == "true":
        call.delivered_at = datetime.now()
        call.save()
        return HttpResponse("Saved")
    else:
        call.delivered_at = None
        call.save()
        return HttpResponse("Deleted")


@login_required
@coordinator_required
def call_comment(request):
    text = request.POST["text"]
    sid = request.POST["sid"]
    call = models.Call.objects.get(twilio_sid=sid)
    call.comment = text
    call.save()
    return HttpResponse("Saved")


@login_required
@coordinator_required
def fetch_calls(request):
    calls = {c.twilio_sid: model_to_dict(c) for c in models.Call.objects.all()}
    return JsonResponse(calls)

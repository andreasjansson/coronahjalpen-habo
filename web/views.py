import pytz
from django.utils.timezone import activate as activate_timezone
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
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
    return render(request, "calls.html", {"calls": calls})


@login_required
@coordinator_required
def call_posted(request):
    posted = request.POST["posted"]
    sid = request.POST["sid"]
    if posted == "true":
        handled = models.HandledCall(twilio_sid=sid)
        handled.save()
        return HttpResponse("Saved")
    else:
        models.HandledCall.objects.filter(twilio_sid=sid).delete()
        return HttpResponse("Deleted")

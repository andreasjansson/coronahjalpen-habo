from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("samordna/samtal", views.manage_calls, name="samtal"),
    path("samordna/alla-samtal", views.manage_all_calls, name="alla-samtal"),
    path("samordna/samtal-postad", views.call_posted, name="samtal-postad"),
    path("samordna/samtal-levererad", views.call_delivered, name="samtal-levererad"),
    path("samordna/samtal-kommentar", views.call_comment, name="samtal-kommentar"),
    path("samordna/samtal-ajax", views.fetch_calls, name="samtal-ajax"),
    path("samordna/statistik", views.stats, name="stats"),
    # social
    path("login/", views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("social-auth/", include("social_django.urls", namespace="social")),
    # users
    path("invites/<str:pk>/", views.invite_detail, name="invite-detail"),
]

urlpatterns += staticfiles_urlpatterns()

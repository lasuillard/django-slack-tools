from django.contrib import admin
from django.urls import include, path

from django_slack_bot.views import SlackEventHandlerView
from testproj.config.slack_app import app

urlpatterns = [
    path("admin/", admin.site.urls),
    path("slack/events", SlackEventHandlerView.as_view(app=app), name="slack_events"),
    path("__debug__/", include("debug_toolbar.urls")),
]

from config.slack_app import app
from django.contrib import admin
from django.urls import path

from django_slack_bot.views import SlackEventHandlerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("slack/events", SlackEventHandlerView.as_view(app=app), name="slack_events"),
]

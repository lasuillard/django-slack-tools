from config.slack_app import get_slack_app
from django.contrib import admin
from django.urls import path

from django_slack_bot.views import SlackEventHandlerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("slack/events", SlackEventHandlerView.as_view(app=get_slack_app), name="slack_events"),
]

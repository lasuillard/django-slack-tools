from django.contrib import admin
from django.urls import path

from django_slack_bot.views import SlackEventHandlerView
from todo.slack_app import app

urlpatterns = [
    path("admin/", admin.site.urls),
    path("slack/events/", SlackEventHandlerView.as_view(app=app)),
]

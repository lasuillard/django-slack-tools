# noqa: D100
from django.contrib import admin

from django_slack_bot.models import SlackMessage

# TODO(lasuillard): Action for (Re)send messages


@admin.register(SlackMessage)
class SlackMessageAdmin(admin.ModelAdmin):
    """Admin for messages."""

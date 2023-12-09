# noqa: D100
from django.contrib import admin

from django_slack_bot.models import Message

# TODO(lasuillard): Action for (Re)send messages


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin for messages."""

# noqa: D100
from django.contrib import admin

from django_slack_bot.models import SlackMessageRecipient


@admin.register(SlackMessageRecipient)
class SlackMessageRecipientAdmin(admin.ModelAdmin):
    """Admin for recipients."""

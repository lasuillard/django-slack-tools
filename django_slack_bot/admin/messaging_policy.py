# noqa: D100
from django.contrib import admin

from django_slack_bot.models import SlackMessagingPolicy


@admin.register(SlackMessagingPolicy)
class SlackMessagingPolicyAdmin(admin.ModelAdmin):
    """Admin for messaging policies."""

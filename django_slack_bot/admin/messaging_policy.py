# noqa: D100
from django.contrib import admin

from django_slack_bot.models import MessagingPolicy


@admin.register(MessagingPolicy)
class MessagingPolicyAdmin(admin.ModelAdmin):
    """Admin for messaging policies."""

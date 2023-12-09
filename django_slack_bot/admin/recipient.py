# noqa: D100
from django.contrib import admin

from django_slack_bot.models import Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Admin for recipients."""

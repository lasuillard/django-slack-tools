# noqa: D100
from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoSlackBotConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_slack_bot.slack_messages"
    verbose_name = _("Slack Messages")

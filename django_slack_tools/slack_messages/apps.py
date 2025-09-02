# noqa: D100
from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoSlackBotConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_slack_tools.slack_messages"
    verbose_name = _("Slack Messages")

    def ready(self) -> None:  # pragma: no cover
        """Auto-discover Celery tasks, if Celery is installed."""
        try:
            import celery  # noqa: F401, PLC0415
        except ImportError:
            pass
        else:
            from . import tasks  # noqa: F401, PLC0415

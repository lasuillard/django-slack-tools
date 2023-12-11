"""Application settings."""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


class AppSettings:
    """Application settings."""

    def __init__(self) -> None:  # noqa: D107
        messaging_backend = getattr(settings, "SLACK_MESSAGING_BACKEND", None)
        if messaging_backend is None:
            msg = "Messaging backend not provided."
            raise ImproperlyConfigured(msg)

        self.SLACK_MESSAGING_BACKEND = import_string(messaging_backend)


app_settings = AppSettings()

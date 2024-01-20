"""Application settings.

In your Django settings, Django Slack Bot expects something like:

"""
from __future__ import annotations

from logging import getLogger
from typing import Any, TypedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from slack_bolt import App

from django_slack_bot.slack_messages.backends.base import BackendBase

APP_SETTINGS_KEY = "DJANGO_SLACK_BOT"
"Django settings key for this application."

logger = getLogger(__name__)


class AppSettings:
    """Application settings."""

    backend: BackendBase

    def __init__(self, settings_dict: ConfigDict | None = None) -> None:
        """Initialize app settings.

        Args:
            settings_dict: Settings dictionary. If `None`, try to load from Django settings (const `APP_SETTINGS_KEY`).
                Defaults to `None`.

        Raises:
            ImproperlyConfigured: Required configuration not provided or is unexpected.
        """
        if not settings_dict:
            settings_dict = getattr(settings, APP_SETTINGS_KEY, None)

        if settings_dict is None:
            msg = "Neither `settings_dict` provided or `DJANGO_SLACK_BOT` settings found in Django settings."
            raise ImproperlyConfigured(msg)

        # Slack app
        slack_app = settings_dict["SLACK_APP"]
        if isinstance(slack_app, str):
            slack_app = import_string(slack_app)

        if callable(slack_app):
            slack_app = slack_app()

        if not isinstance(slack_app, App):
            msg = "Provided `SLACK_APP` config is not Slack app."
            raise ImproperlyConfigured(msg)

        self._slack_app = slack_app

        # Find backend class
        messaging_backend = import_string(settings_dict["BACKEND"]["NAME"])
        if not issubclass(messaging_backend, BackendBase):
            msg = "Provided backend is not a subclass of `{qualified_path}` class.".format(
                qualified_path=f"{BackendBase.__module__}.{BackendBase.__name__}",
            )
            raise ImproperlyConfigured(msg)

        # Initialize with provided options
        self.backend = messaging_backend(**settings_dict["BACKEND"]["OPTIONS"])

    @property
    def slack_app(self) -> App:
        """Registered Slack app or `None`."""
        return self._slack_app


app_settings = AppSettings()


class ConfigDict(TypedDict):
    """Root config dict."""

    SLACK_APP: App | str | None
    "Import string to Slack app. Used for workspace-related stuffs."

    BACKEND: BackendConfig
    "Nested backend config."


class BackendConfig(TypedDict):
    """Backend config dict."""

    NAME: str
    "Import path to backend class."

    OPTIONS: dict[str, Any]
    "Options to pass to backend class on initialization."

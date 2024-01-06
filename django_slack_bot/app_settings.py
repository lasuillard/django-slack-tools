"""Application settings.

In your Django settings, Django Slack Bot expects something like:

"""
from __future__ import annotations

from typing import Any, TypedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .backends import BackendBase

APP_SETTINGS_KEY = "DJANGO_SLACK_BOT"
"Django settings key for this application."


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

        # Find backend class
        messaging_backend = import_string(settings_dict["BACKEND"]["NAME"])
        if not issubclass(messaging_backend, BackendBase):
            msg = "Provided backend is not a subclass of `{qualified_path}` class.".format(
                qualified_path=f"{BackendBase.__module__}.{BackendBase.__name__}",
            )
            raise ImproperlyConfigured(msg)

        # Initialize with provided options
        self.backend = messaging_backend(**settings_dict["BACKEND"]["OPTIONS"])


app_settings = AppSettings()


class ConfigDict(TypedDict):
    """Root config dict."""

    BACKEND: BackendConfig
    "Nested backend config."


class BackendConfig(TypedDict):
    """Backend config dict."""

    NAME: str
    "Import path to backend class."

    OPTIONS: dict[str, Any]
    "Options to pass to backend class on initialization."

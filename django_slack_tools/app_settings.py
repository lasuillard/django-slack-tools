"""Application settings."""
# flake8: noqa: UP007

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, TypedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from slack_bolt import App
from typing_extensions import NotRequired, Self

from django_slack_tools.utils.import_helper import LazyInitSpec, lazy_init

if TYPE_CHECKING:
    from django_slack_tools.messenger.shortcuts import Messenger

logger = getLogger(__name__)


class SettingsDict(TypedDict):
    """Dictionary input for app settings."""

    slack_app: str
    messengers: NotRequired[dict[str, LazyInitSpec]]


class AppSettings:
    """Application settings."""

    slack_app: App
    messengers: dict[str, Messenger]

    def __init__(self, slack_app: App, messengers: dict[str, Messenger]) -> None:  # noqa: D107
        if not isinstance(slack_app, App):
            msg = f"Expected {App!s} instance, got {type(slack_app)}"
            raise TypeError(msg)

        self.slack_app = slack_app
        self.messengers = messengers

    @classmethod
    def from_dict(cls, settings_dict: SettingsDict) -> Self:
        """Initialize settings from a dictionary."""
        try:
            slack_app = import_string(settings_dict["slack_app"])
            messengers = {
                name: cls._create_messenger(spec) for name, spec in settings_dict.get("messengers", {}).items()
            }
            return cls(
                slack_app=slack_app,
                messengers=messengers,
            )
        except Exception as err:
            msg = f"Couldn't initialize app settings: {err!s}"
            raise ImproperlyConfigured(msg) from err

    @classmethod
    def _create_messenger(cls, spec: LazyInitSpec) -> Messenger:
        class_ = import_string(spec["class"])
        args, kwargs = spec.get("args", ()), spec.get("kwargs", {})

        # Lazy-init all the things
        kwargs = kwargs.copy()
        kwargs["template_loaders"] = [lazy_init(tl) for tl in kwargs["template_loaders"]]
        kwargs["middlewares"] = [lazy_init(tl) for tl in kwargs["middlewares"]]
        kwargs["messaging_backend"] = lazy_init(kwargs["messaging_backend"])

        # Create the messenger
        return class_(*args, **kwargs)  # type: ignore[no-any-return]


def get_settings_from_django(settings_key: str = "DJANGO_SLACK_TOOLS") -> AppSettings:
    """Get application settings."""
    django_settings: SettingsDict = getattr(settings, settings_key)
    return AppSettings.from_dict(django_settings or {})


app_settings = get_settings_from_django()


def get_messenger(name: str | None = None) -> Messenger:
    """Get a messenger instance by name."""
    name = name or "default"
    return app_settings.messengers[name]

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ImproperlyConfigured
from slack_bolt import App

from django_slack_tools.app_settings import AppSettings, get_settings_from_django
from django_slack_tools.slack_messages.messenger import Messenger

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper

    from django_slack_tools.app_settings import SettingsDict


# Config fixtures to run in parametrize (map of test id to config dictionary)
config_fixtures: dict[str, SettingsDict] = {
    "dummy backend": {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [],
                    "middlewares": [],
                    "messaging_backend": "django_slack_tools.slack_messages.backends.DummyBackend",
                },
            },
        },
    },
    "logging backend": {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [],
                    "middlewares": [],
                    "messaging_backend": "django_slack_tools.slack_messages.backends.LoggingBackend",
                },
            },
        },
    },
    "slack backend": {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [],
                    "middlewares": [],
                    "messaging_backend": {
                        "class": "django_slack_tools.slack_messages.backends.SlackBackend",
                        "kwargs": {
                            "slack_app": "testproj.config.slack_app.app",
                        },
                    },
                },
            },
        },
    },
    "slack redirect backend": {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [],
                    "middlewares": [],
                    "messaging_backend": {
                        "class": "django_slack_tools.slack_messages.backends.SlackRedirectBackend",
                        "kwargs": {
                            "slack_app": "testproj.config.slack_app.app",
                            "redirect_channel": "some-redirect-channel",
                        },
                    },
                },
            },
        },
    },
    "django db": {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [
                        "django_slack_tools.slack_messages.template_loaders.DjangoTemplateLoader",
                        "django_slack_tools.slack_messages.template_loaders.DjangoPolicyTemplateLoader",
                    ],
                    "middlewares": [
                        {
                            "class": "django_slack_tools.slack_messages.middlewares.DjangoDatabasePolicyHandler",
                            "kwargs": {
                                "messenger": "default",
                            },
                        },
                        "django_slack_tools.slack_messages.middlewares.DjangoDatabasePersister",
                    ],
                    "messaging_backend": {
                        "class": "django_slack_tools.slack_messages.backends.SlackBackend",
                        "kwargs": {
                            "slack_app": "testproj.config.slack_app.app",
                        },
                    },
                },
            },
        },
    },
}

# Save decorator for reuse, as not all test in suite requires this
settings_dict_parametrizer = pytest.mark.parametrize(
    argnames="settings_dict",
    argvalues=config_fixtures.values(),
    ids=config_fixtures.keys(),
)

# For import testing
not_slack_app = -1


class TestAppSettings:
    def _assert_app_settings(self, app_settings: AppSettings) -> None:
        assert isinstance(app_settings.slack_app, App)
        assert all(isinstance(messenger, Messenger) for messenger in app_settings.messengers.values())

    @settings_dict_parametrizer
    def test_dict_config(self, settings_dict: SettingsDict) -> None:
        app_settings = AppSettings.from_dict(settings_dict)
        self._assert_app_settings(app_settings)

    @settings_dict_parametrizer
    def test_django_config(self, settings: SettingsWrapper, settings_dict: SettingsDict) -> None:
        settings.DJANGO_SLACK_TOOLS = None
        with pytest.raises(ImproperlyConfigured, match=r"^Couldn't initialize app settings: .+"):
            get_settings_from_django()

        settings.DJANGO_SLACK_TOOLS = settings_dict
        app_settings = get_settings_from_django()
        self._assert_app_settings(app_settings)

    def test_bad_config_not_slack_app(self) -> None:
        with pytest.raises(
            ImproperlyConfigured,
            match="Expected <class 'slack_bolt.app.app.App'> instance, got <class 'int'>",
        ):
            AppSettings.from_dict(
                {
                    "slack_app": "tests.test_app_settings.not_slack_app",
                    "messengers": {},
                },
            )

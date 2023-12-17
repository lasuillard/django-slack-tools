from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ImproperlyConfigured

from django_slack_bot.app_settings import AppSettings
from django_slack_bot.backends import DummyBackend

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper

    from django_slack_bot.app_settings import ConfigDict


# Config fixtures to run in parametrize
config_fixtures: dict[str, ConfigDict] = {
    "dummy_backend": {
        "BACKEND": {
            "NAME": "django_slack_bot.backends.DummyBackend",
            "OPTIONS": {},
        },
    },
    # TODO(lasuillard): Test with other backend configurations
    # "logging_backend": {},  # noqa: ERA001
    # "slack_backend": {},  # noqa: ERA001
    # "slack_redirect_backend": {},  # noqa: ERA001
}


@pytest.mark.parametrize(
    argnames="settings_dict",
    argvalues=config_fixtures.values(),
    ids=config_fixtures.keys(),
)
class AppSettingsTests:
    def _assert_app_settings(self, app_settings: AppSettings) -> None:
        assert isinstance(app_settings.backend, DummyBackend)

    def test_dict_config(self, settings_dict: ConfigDict) -> None:
        app_settings = AppSettings(settings_dict)
        self._assert_app_settings(app_settings)

    def test_django_config(self, settings: SettingsWrapper, settings_dict: ConfigDict) -> None:
        settings.DJANGO_SLACK_BOT = None
        with pytest.raises(ImproperlyConfigured, match=r"^Neither `.+` provided or `.+` settings found"):
            AppSettings()

        settings.DJANGO_SLACK_BOT = settings_dict
        app_settings = AppSettings()
        self._assert_app_settings(app_settings)

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.messenger import Messenger
from django_slack_tools.slack_messages.middlewares import DjangoDatabasePersister, DjangoDatabasePolicyHandler

if TYPE_CHECKING:
    from slack_bolt import App

    from django_slack_tools.app_settings import SettingsDict


@pytest.fixture(scope="session")
def app_settings() -> SettingsDict:
    return {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "test-django-middleware": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [],
                    "middlewares": [],
                    "messaging_backend": {
                        "class": "django_slack_tools.slack_messages.backends.DummyBackend",
                        "kwargs": {},
                    },
                },
            },
        },
    }


@pytest.mark.usefixtures("override_app_settings")
class TestDjangoDatabasePersister:
    def test_instance_creation(self, slack_app: App) -> None:
        """Test various instance creation scenarios."""
        DjangoDatabasePersister(slack_app=None, get_permalink=False)
        with pytest.raises(
            ValueError,
            match="`slack_app` must be an instance of `App` if `get_permalink` is set `True`.",
        ):
            DjangoDatabasePersister(slack_app=None, get_permalink=True)

        DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)
        DjangoDatabasePersister(slack_app=slack_app, get_permalink=False)


@pytest.mark.usefixtures("override_app_settings")
class TestDjangoDatabasePolicyHandler:
    def test_instance_creation(self) -> None:
        """Test various instance creation scenarios."""
        messenger = Messenger(template_loaders=[], middlewares=[], messaging_backend=DummyBackend())

        middleware = DjangoDatabasePolicyHandler(messenger=messenger, auto_create_policy=False)
        assert middleware.messenger == messenger

        middleware = DjangoDatabasePolicyHandler(messenger=messenger, auto_create_policy=True)
        assert middleware.messenger == messenger

        middleware = DjangoDatabasePolicyHandler(messenger="test-django-middleware", auto_create_policy=False)
        assert isinstance(middleware.messenger, Messenger)

        middleware = DjangoDatabasePolicyHandler(messenger="test-django-middleware", auto_create_policy=True)
        assert isinstance(middleware.messenger, Messenger)

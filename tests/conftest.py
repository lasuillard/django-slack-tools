from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from celery.contrib.testing.worker import start_worker
from slack_bolt import App
from testcontainers.redis import RedisContainer

from django_slack_tools.app_settings import AppSettings
from testproj.config.celery import app

if TYPE_CHECKING:
    from collections.abc import Iterator

    from django_slack_tools.app_settings import SettingsDict


@pytest.fixture(scope="session")
def slack_app() -> App:
    """Dummy Slack app fixture. It won't work."""
    return App(
        token="stupid-sandwich",  # noqa: S106
        signing_secret="peanut-butter",  # noqa: S106
        token_verification_enabled=False,
    )


@pytest.fixture
def mock_slack_client() -> Iterator[mock.Mock]:
    """Mock `slack_bolt.App.client`."""
    with mock.patch("slack_bolt.App.client") as m:
        yield m


@pytest.fixture(scope="session")
def app_settings() -> SettingsDict:
    """Default app settings fixture. Each test suite should override it for practical test cases."""
    return {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.messenger.shortcuts.Messenger",
                "kwargs": {
                    "template_loaders": [],
                    "middlewares": [],
                    "messaging_backend": "django_slack_tools.messenger.shortcuts.DummyBackend",
                },
            },
        },
    }


@pytest.fixture
def override_app_settings(app_settings: SettingsDict) -> Iterator[None]:
    """Override app settings with settings dict returned by `app_settings` fixture."""
    override = AppSettings.from_dict(app_settings)
    with mock.patch("django_slack_tools.app_settings.app_settings", override):
        yield


@pytest.fixture(scope="session")
def redis_url() -> Iterator[str]:
    with RedisContainer("redis:7-alpine") as container:
        yield f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}"


@pytest.fixture(scope="module")
def celery_worker(redis_url: str) -> Iterator[None]:
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("CELERY_BROKER_URL", redis_url)
    with start_worker(app, perform_ping_check=False, pool="threads", concurrency=4):
        yield

    monkeypatch.undo()

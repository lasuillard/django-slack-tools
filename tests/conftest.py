from __future__ import annotations

from typing import Generator
from unittest import mock

import pytest
from slack_bolt import App


@pytest.fixture(scope="session")
def vcr_config() -> dict:
    """Fixture for providing config to pytest-recording."""
    return {
        "allowed_hosts": ["localhost"],
    }


@pytest.fixture(scope="session")
def slack_app() -> App:
    """Dummy Slack app fixture. It won't work."""
    return App(
        token="stupid-sandwich",  # noqa: S106
        signing_secret="peanut-butter",  # noqa: S106
        token_verification_enabled=False,
    )


@pytest.fixture()
def mock_slack_client() -> Generator[mock.Mock, None, None]:
    """Mock `slack_bolt.App.client`."""
    with mock.patch("slack_bolt.App.client") as m:
        yield m

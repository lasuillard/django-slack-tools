from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest
from slack_bolt import App

if TYPE_CHECKING:
    from collections.abc import Iterator


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

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import pytest

from django_slack_bot.app_settings import app_settings
from django_slack_bot.slack_messages.backends import SlackRedirectBackend

if TYPE_CHECKING:
    from slack_bolt import App


@pytest.fixture()
def redirect_slack(
    slack_app: App,
    slack_channel: str,
) -> Generator[None, None, None]:
    """Replace app backend to Slack redirect backend temporarily.

    CAUTION: This will actually send messages to specified channel with given bot credentials.

    It replaces global backend with `SlackRedirectBackend` with app instance taken from `slack_app` fixture.
    In addition, `"TEST_SLACK_CHANNEL"` environment variable should be provided.
    """
    old_backend = app_settings.backend

    # Swap app global backend temporarily
    app_settings.backend = SlackRedirectBackend(
        slack_app=slack_app,
        redirect_channel=slack_channel,
    )
    yield None

    app_settings.backend = old_backend

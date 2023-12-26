from __future__ import annotations

import os
from typing import TYPE_CHECKING, Generator

import pytest
from slack_bolt import App

from django_slack_bot.app_settings import app_settings
from django_slack_bot.backends import SlackRedirectBackend

if TYPE_CHECKING:
    from pytest import FixtureRequest  # noqa: PT013


@pytest.fixture(scope="session")
def vcr_config() -> dict:
    return {
        # Filter out authorization header in request containing Slack token
        "filter_headers": ["authorization"],
    }


@pytest.fixture(scope="session")
def slack_app(request: FixtureRequest) -> App:
    """Actual Slack application for some tests.

    If updating VCR cassettes (`--record-mode` other than `none`) Slack app credentials need to be provided.
    Each token and signing secret load from environment variable `"TEST_SLACK_BOT_TOKEN"` and `"TEST_SLACK_SIGNING_SECRET"`.
    """  # noqa: E501
    vcr_mode = request.config.getoption("--record-mode")
    if vcr_mode in ("none", None):
        return App(
            token="stupid-sandwitch",  # noqa: S106
            signing_secret="peanut-butter",  # noqa: S106
            token_verification_enabled=False,
        )

    token = os.environ["TEST_SLACK_BOT_TOKEN"]
    signing_secret = os.environ["TEST_SLACK_SIGNING_SECRET"]
    return App(token=token, signing_secret=signing_secret, token_verification_enabled=False)


@pytest.fixture()
def slack_redirect_backend(request: FixtureRequest, slack_app: App) -> Generator[SlackRedirectBackend, None, None]:
    """Use Slack redirect backend for a test.

    CAUTION: This will actually send messages to specified channel with given bot credentials.

    It replaces global backend with `SlackRedirectBackend` with app instance taken from `slack_app` fixture.
    In addition, `"TEST_SLACK_REDIRECT_CHANNEL"` environment variable should be provided.
    """
    vcr_mode = request.config.getoption("--record-mode")
    redirect_channel = "redirect-channel"
    if vcr_mode not in ("none", None):
        redirect_channel = os.environ["TEST_SLACK_REDIRECT_CHANNEL"]

    old_backend = app_settings.backend

    # Swap app global backend temporarily
    app_settings.backend = SlackRedirectBackend(
        slack_app=slack_app,
        redirect_channel=redirect_channel,
    )
    yield app_settings.backend

    app_settings.backend = old_backend

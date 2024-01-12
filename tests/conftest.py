from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING, Generator

import pytest
from slack_bolt import App

from django_slack_bot.app_settings import app_settings
from django_slack_bot.backends import SlackRedirectBackend

if TYPE_CHECKING:
    from pytest import FixtureRequest  # noqa: PT013
    from vcr.request import Request


@pytest.fixture(scope="session")
def vcr_config() -> dict:
    """VCR cassette configurations.

    To minimize changes on cassettes by test update, some headers and data fields are reduced, removed or
    substituted.
    """

    def scrub_id(s: str) -> str:
        return re.sub(r"[0-9A-Z]{11}", "<REDACTED>", s)

    def before_record_request(request: Request) -> Request:
        # TODO(lasuillard): Better scrubbing
        try:
            request.headers = {}  # No header needed in tests (yet)
            request.body = scrub_id(request.body.decode())
        except:  # noqa: S110, E722
            pass

        return request

    def before_record_response(response: dict) -> dict:
        # TODO(lasuillard): Better scrubbing
        try:
            response["headers"] = {}  # No header needed in tests (yet)

            # Filter response data
            body: dict = json.loads(response["body"]["string"])
            body["message"]["bot_profile"] = {}
            response["body"]["string"] = scrub_id(json.dumps(body)).encode()
        except:  # noqa: S110, E722
            pass

        return response

    return {
        "before_record_request": before_record_request,
        "before_record_response": before_record_response,
    }


# TODO(lasuillard): Test settings quite dirty and not straightforward; need refactor


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


@pytest.fixture(scope="session")
def slack_channel(request: FixtureRequest) -> str:
    vcr_mode = request.config.getoption("--record-mode")
    if vcr_mode in ("none", None):
        return "test-channel"

    return os.environ["TEST_SLACK_CHANNEL"]


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

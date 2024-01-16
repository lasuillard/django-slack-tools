from __future__ import annotations

import pytest
from slack_bolt import App


@pytest.fixture(scope="session")
def vcr_config() -> dict:
    return {
        "allowed_hosts": ["localhost"],
    }


@pytest.fixture(scope="session")
def slack_app() -> App:
    return App(
        token="stupid-sandwitch",  # noqa: S106
        signing_secret="peanut-butter",  # noqa: S106
        token_verification_enabled=False,
    )

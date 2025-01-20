from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from django_slack_tools.slack_messages.response import MessageResponse
from django_slack_tools.slack_messages.shortcuts import slack_message

from ._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock

    from django_slack_tools.app_settings import SettingsDict

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="session")
def app_settings() -> SettingsDict:
    return {
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
    }


@pytest.mark.usefixtures("override_app_settings")
def test_slack_message(mock_slack_client: Mock) -> None:
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
    response = slack_message("whatever-channel", template="greet.xml", context={"greet": "Hello, World!"})

    assert isinstance(response, MessageResponse)
    assert (request := response.request)
    assert request.model_dump() == {
        "body": {
            "attachments": None,
            "blocks": [{"text": {"text": "Hello, World!,", "type": "mrkdwn"}, "type": "section"}],
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "text": None,
            "username": None,
        },
        "channel": "whatever-channel",
        "context": {
            "greet": "Hello, World!",
        },
        "header": {
            "mrkdwn": None,
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        },
        "id_": mock.ANY,
        "template_key": "greet.xml",
    }
    assert response.error is None
    assert response.data
    assert response.ts
    assert response.parent_ts is None

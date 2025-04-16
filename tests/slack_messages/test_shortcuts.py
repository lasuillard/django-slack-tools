from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from django_slack_tools.messenger.shortcuts import MessageResponse
from django_slack_tools.slack_messages.shortcuts import slack_message

from ._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock

    from django_slack_tools.app_settings import SettingsDict

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("override_app_settings"),
]


@pytest.fixture(scope="session")
def app_settings() -> SettingsDict:
    return {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "default": {
                "class": "django_slack_tools.messenger.shortcuts.Messenger",
                "kwargs": {
                    "template_loaders": [
                        "django_slack_tools.slack_messages.messenger.DjangoTemplateLoader",
                        "django_slack_tools.slack_messages.messenger.DjangoPolicyTemplateLoader",
                    ],
                    "middlewares": [
                        "django_slack_tools.slack_messages.messenger.DjangoDatabasePersister",
                    ],
                    "messaging_backend": {
                        "class": "django_slack_tools.messenger.shortcuts.SlackBackend",
                        "kwargs": {
                            "slack_app": "testproj.config.slack_app.app",
                        },
                    },
                },
            },
        },
    }


def test_slack_message_simplest_message(mock_slack_client: Mock) -> None:
    # Arrange
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

    # Act
    response = slack_message("whatever-channel", message="Hello, World!")

    # Assert
    assert isinstance(response, MessageResponse)
    assert (request := response.request)
    assert request.model_dump() == {
        "body": {
            "attachments": None,
            "blocks": None,
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "text": "Hello, World!",
            "username": None,
        },
        "channel": "whatever-channel",
        "context": {},
        "header": {
            "mrkdwn": None,
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        },
        "id_": mock.ANY,
        "template_key": None,
    }

    assert response.error is None
    assert response.data
    assert response.ts
    assert response.parent_ts is None


def test_slack_message_with_template(mock_slack_client: Mock) -> None:
    # Arrange
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

    # Act
    response = slack_message("whatever-channel", template="greet.xml", context={"greet": "Hello, World!"})

    # Assert
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


def test_slack_message_mutually_exclusive_arguments(mock_slack_client: Mock) -> None:
    # Arrange
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

    # Act & Assert
    with pytest.raises(ValueError, match="Either `template` or `message` must be set, but not both."):
        slack_message(  # type: ignore[call-overload]
            "whatever-channel",
            message="Hello, World!",
            template="greet.xml",
            context={"greet": "Hello, World!"},
        )

    mock_slack_client.chat_postMessage.assert_not_called()

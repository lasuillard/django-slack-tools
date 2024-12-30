from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_tools.slack_messages.backends import SlackBackend, SlackRedirectBackend
from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest
from django_slack_tools.slack_messages.response import MessageResponse
from tests.slack_messages._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock

    from slack_bolt import App


class TestSlackBackend:
    # TODO(lasuillard): Test `.__init__()` for import string & callable

    pytestmark = pytest.mark.django_db()

    @pytest.fixture
    def backend(self, slack_app: App) -> SlackBackend:
        return SlackBackend(slack_app=slack_app)

    def test_deliver(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        """Test sending message."""
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        request = MessageRequest(
            channel="test-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
        )
        response = backend.deliver(request)

        assert isinstance(response, MessageResponse)
        assert response.request is request
        assert response.ok is True
        assert response.error is None
        assert response.data
        assert response.ts
        assert response.parent_ts is None


class TestSlackRedirectBackend:
    pytestmark = pytest.mark.django_db()

    @pytest.fixture
    def backend(self, slack_app: App) -> SlackRedirectBackend:
        return SlackRedirectBackend(slack_app=slack_app, redirect_channel="test-redirect-channel")

    def test_deliver(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
        """Test sending message."""
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        request = MessageRequest(
            channel="test-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
        )
        response = backend.deliver(request)

        assert isinstance(response, MessageResponse)
        assert response.request is request
        assert response.ok is True
        assert response.error is None
        assert response.data
        assert response.ts
        assert response.parent_ts is None

    def test_send_message(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        request = MessageRequest(
            channel="whatever-this-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
        )
        response = backend.deliver(request)

        assert isinstance(response, MessageResponse)
        mock_slack_client.chat_postMessage.assert_called_once_with(
            channel="test-redirect-channel",
            mrkdwn=None,
            parse=None,
            reply_broadcast=None,
            thread_ts=None,
            unfurl_links=None,
            unfurl_media=None,
            attachments=[
                {
                    "color": "#eb4034",
                    "text": ":warning:  This message was originally sent to channel *whatever-this-channel* but redirected here.",  # noqa: E501
                },
            ],
            blocks=None,
            text="Hello, World!",
            icon_emoji=None,
            icon_url=None,
            metadata=None,
            username=None,
        )

    def test_send_message_no_inform_redirect(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
        backend.inform_redirect = False
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        request = MessageRequest(
            channel="whatever-this-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=MessageBody(text="Hello, World!"),
        )
        response = backend.deliver(request)

        assert isinstance(response, MessageResponse)
        mock_slack_client.chat_postMessage.assert_called_once_with(
            channel="test-redirect-channel",
            mrkdwn=None,
            parse=None,
            reply_broadcast=None,
            thread_ts=None,
            unfurl_links=None,
            unfurl_media=None,
            attachments=None,
            blocks=None,
            text="Hello, World!",
            icon_emoji=None,
            icon_url=None,
            metadata=None,
            username=None,
        )

    def test_make_inform_attachment(self, backend: SlackRedirectBackend) -> None:
        attachment = backend._make_inform_attachment(original_channel="test-original-channel")
        assert attachment == {
            "color": "#eb4034",
            "text": ":warning:  This message was originally sent to channel *test-original-channel* but redirected here.",  # noqa: E501
        }

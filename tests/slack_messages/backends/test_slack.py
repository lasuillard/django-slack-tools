from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from slack_sdk.errors import SlackApiError

from django_slack_tools.slack_messages.backends import SlackBackend, SlackRedirectBackend
from django_slack_tools.slack_messages.models import SlackMessage
from django_slack_tools.utils.slack import MessageBody, MessageHeader
from tests._factories import SlackApiErrorFactory, SlackResponseFactory
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

    def test_send_message(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        """Test sending message."""
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        message = backend.send_message(
            backend.prepare_message(
                channel="test-channel",
                header=MessageHeader(),
                body=MessageBody(text="Hello, World!"),
            ),
            raise_exception=True,
            get_permalink=False,
        )

        assert isinstance(message, SlackMessage)
        assert message.request
        assert "Authorization" not in message.request["headers"]
        assert message.response
        assert not message.exception

    def test_send_message_error_response(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        """Test `raise_exception` flag."""
        message = SlackMessage(channel="test-channel", header={}, body={})
        mock_slack_client.chat_postMessage.side_effect = SlackApiErrorFactory()

        # Should re-raise the exception
        with pytest.raises(SlackApiError):
            backend.send_message(message, raise_exception=True, get_permalink=False)

        # Won't raise
        backend.send_message(message, raise_exception=False, get_permalink=False)

    def test_send_message_unexpected_error(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        """Test `raise_exception` flag."""
        message = SlackMessage(channel="test-channel", header={}, body={})

        class UnexpectedError(Exception): ...

        mock_slack_client.chat_postMessage.side_effect = UnexpectedError()

        # Should re-raise the exception
        with pytest.raises(UnexpectedError):
            backend.send_message(message, raise_exception=True, get_permalink=False)

        # Won't raise
        backend.send_message(message, raise_exception=False, get_permalink=False)

    def test_send_message_permalink(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        """Test permalink."""
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
        mock_slack_client.chat_getPermalink.return_value = SlackResponseFactory(
            data={"ok": True, "permalink": "https://..."},
        )

        message = backend.send_message(
            message=SlackMessage(channel="test-channel", header={}, body={}),
            raise_exception=False,
            get_permalink=True,
        )

        assert isinstance(message, SlackMessage)
        assert message.permalink == "https://..."

    def test_get_permalink(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        message = SlackMessage(channel="test-channel", ts="0000.0000")
        mock_slack_client.chat_getPermalink.return_value = SlackResponseFactory(
            data={"ok": True, "permalink": "https://..."},
        )
        permalink = backend._get_permalink(message=message, raise_exception=True)
        assert permalink == "https://..."

        # If error, returns empty string
        mock_slack_client.chat_getPermalink.side_effect = SlackApiErrorFactory()
        permalink = backend._get_permalink(message=message, raise_exception=False)
        assert permalink == ""

        # Re-raise exception if flag set
        mock_slack_client.chat_getPermalink.side_effect = SlackApiErrorFactory()
        with pytest.raises(SlackApiError):
            backend._get_permalink(message=message, raise_exception=True)

        # Raise exception if message timestamp is not set
        with pytest.raises(ValueError, match="Message timestamp is not set, can't retrieve permalink."):
            backend._get_permalink(message=SlackMessage(channel="test-channel", ts=None), raise_exception=True)


class TestSlackRedirectBackend:
    pytestmark = pytest.mark.django_db()

    @pytest.fixture
    def backend(self, slack_app: App) -> SlackRedirectBackend:
        return SlackRedirectBackend(slack_app=slack_app, redirect_channel="test-redirect-channel")

    def test_send_message(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        message = backend.send_message(
            backend.prepare_message(
                channel="whatever-this-channel",
                header=MessageHeader(),
                body=MessageBody(text="Hello, World!"),
            ),
            raise_exception=True,
            get_permalink=False,
        )

        assert isinstance(message, SlackMessage)

    def test_send_message_no_redirect(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
        backend.inform_redirect = False
        mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()

        message = backend.send_message(
            backend.prepare_message(
                channel="whatever-this-channel",
                header=MessageHeader(),
                body=MessageBody(text="Hello, World!"),
            ),
            raise_exception=True,
            get_permalink=False,
        )

        assert message.body == {
            "text": "Hello, World!",
            "attachments": None,
            "blocks": None,
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "username": None,
        }

    def test_prepare_message(self, backend: SlackRedirectBackend) -> None:
        message = backend.prepare_message(
            channel="test-original-channel",
            header=MessageHeader(),
            body=MessageBody(
                attachments=[{"text": "Django Slack Tools"}],
            ),
        )
        assert message.body == {
            "text": None,
            "attachments": [
                {
                    "color": "#eb4034",
                    "text": ":warning:  This message was originally sent to channel *test-original-channel* but redirected here.",  # noqa: E501
                },
                {"text": "Django Slack Tools"},
            ],
            "blocks": None,
            "icon_emoji": None,
            "icon_url": None,
            "metadata": None,
            "username": None,
        }

    def test_make_inform_attachment(self, backend: SlackRedirectBackend) -> None:
        attachment = backend._make_inform_attachment(original_channel="test-original-channel")
        assert attachment == {
            "color": "#eb4034",
            "text": ":warning:  This message was originally sent to channel *test-original-channel* but redirected here.",  # noqa: E501
        }

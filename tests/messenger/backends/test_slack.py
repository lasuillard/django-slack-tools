from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from slack_bolt import App

from django_slack_tools.messenger.shortcuts import (
    MessageBody,
    MessageHeader,
    MessageRequest,
    MessageResponse,
    SlackBackend,
    SlackRedirectBackend,
)
from tests._factories import SlackApiErrorFactory
from tests.slack_messages._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock


# Values for import testing
_slack_app = App(
    token="stupid-sandwich",  # noqa: S106
    signing_secret="peanut-butter",  # noqa: S106
    token_verification_enabled=False,
)
_not_slack_app = -1


class TestSlackBackend:
    pytestmark = pytest.mark.django_db()

    @pytest.fixture
    def backend(self, slack_app: App) -> SlackBackend:
        return SlackBackend(slack_app=slack_app)

    def test_instance_creation(self) -> None:
        assert SlackBackend(slack_app="tests.messenger.backends.test_slack._slack_app")
        assert SlackBackend(slack_app=_slack_app)
        with pytest.raises(
            TypeError,
            match="Expected <class 'slack_bolt.app.app.App'> instance, got <class 'int'>",
        ):
            SlackBackend(slack_app="tests.messenger.backends.test_slack._not_slack_app")

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

    def test_deliver_request_body_required(self, backend: SlackBackend) -> None:
        request = MessageRequest(
            channel="test-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=None,
        )
        with pytest.raises(ValueError, match="Message body is required."):
            backend.deliver(request)

    def test_deliver_remote_api_error(self, backend: SlackBackend, mock_slack_client: Mock) -> None:
        """Test sending message with error."""
        mock_slack_client.chat_postMessage.side_effect = SlackApiErrorFactory()

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
        assert response.ok is False
        assert response.error
        assert response.data == {
            "ok": False,
        }
        assert response.ts is None
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
                    "text": ":warning:  This message was originally sent to channel *test-channel* but redirected here.",  # noqa: E501
                },
            ],
            blocks=None,
            text="Hello, World!",
            icon_emoji=None,
            icon_url=None,
            metadata=None,
            username=None,
        )

    def test_deliver_request_body_required(self, backend: SlackRedirectBackend) -> None:
        request = MessageRequest(
            channel="test-channel",
            template_key="__any__",
            context={},
            header=MessageHeader(),
            body=None,
        )
        with pytest.raises(ValueError, match="Message body is required."):
            backend.deliver(request)

    def test_deliver_remote_api_error(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
        """Test sending message with error."""
        mock_slack_client.chat_postMessage.side_effect = SlackApiErrorFactory()

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
        assert response.ok is False
        assert response.error
        assert response.data == {
            "ok": False,
        }
        assert response.ts is None
        assert response.parent_ts is None

    def test_deliver_disable_inform_redirect(self, backend: SlackRedirectBackend, mock_slack_client: Mock) -> None:
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

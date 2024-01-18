from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest
from slack_sdk.errors import SlackApiError

from django_slack_bot.slack_messages.backends import SlackBackend, SlackRedirectBackend
from django_slack_bot.slack_messages.models import SlackMessage
from django_slack_bot.utils.slack import MessageBody, MessageHeader
from tests._factories import SlackResponseFactory
from tests.slack_messages._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from slack_bolt import App


class TestSlackBackend:
    # TODO(lasuillard): Test `.__init__()` for import string & callable

    pytestmark = pytest.mark.django_db()

    @pytest.fixture(scope="class")
    def backend(self, slack_app: App) -> SlackBackend:
        return SlackBackend(slack_app=slack_app)

    def test_send_message(self, backend: SlackBackend) -> None:
        """Test sending message."""
        with mock.patch("slack_bolt.App.client") as m:
            m.chat_postMessage.return_value = SlackMessageResponseFactory()
            msg = backend.send_message(
                channel="test-channel",
                header=MessageHeader(),
                body=MessageBody(text="Hello, World!"),
                raise_exception=True,
            )

        assert isinstance(msg, SlackMessage)
        assert msg.request
        assert "Authorization" not in msg.request["headers"]
        assert msg.response
        assert not msg.exception

    def test_send_message_required_params_if_no_prepared_message(self, backend: SlackBackend) -> None:
        """Test when sending message without prepared message, all required params must be given."""
        kwargs = {
            "channel": "test-channel",
            "header": MessageHeader(),
            "body": MessageBody(text="Hello, World!"),
        }
        for key in kwargs:
            kwargs_copy = kwargs.copy()
            del kwargs_copy[key]
            with pytest.raises(
                TypeError,
                match=(
                    "Call signature mismatch for overload."
                    " If `message` not provided, `channel`, `header` and `body` all must given."
                ),
            ):
                backend.send_message(
                    **kwargs_copy,  # type: ignore[arg-type]
                    raise_exception=True,
                )

    def test_send_message_prepared_message(self, backend: SlackBackend) -> None:
        """Test sending prepared message."""
        prepared_msg = SlackMessage(channel="test-channel", header={}, body={})
        with mock.patch("slack_bolt.App.client") as m:
            m.chat_postMessage.return_value = SlackMessageResponseFactory()
            msg = backend.send_message(message=prepared_msg, raise_exception=True)

        assert isinstance(msg, SlackMessage)

    def test_send_message_error_response(self, backend: SlackBackend) -> None:
        """Test `raise_exception` flag."""
        prepared_msg = SlackMessage(channel="test-channel", header={}, body={})
        with mock.patch("slack_bolt.App.client") as m:
            m.chat_postMessage.side_effect = SlackApiError(
                "Something went wrong",
                response=SlackResponseFactory(data={"ok": False}),
            )
            # Re-raises exception
            with pytest.raises(SlackApiError):
                backend.send_message(message=prepared_msg, raise_exception=True)

            # Won't raise
            backend.send_message(message=prepared_msg, raise_exception=False)

    # TODO(lasuillard): Test permalink


class TestSlackRedirectBackend:
    pytestmark = pytest.mark.django_db()

    def test_send_message(self, slack_app: App) -> None:
        backend = SlackRedirectBackend(slack_app=slack_app, redirect_channel="test-redirect-channel")
        with mock.patch("slack_bolt.App.client") as m:
            m.chat_postMessage.return_value = SlackMessageResponseFactory()
            msg = backend.send_message(
                channel="whatever-this-channel",
                header=MessageHeader(),
                body=MessageBody(text="Hello, World!"),
                raise_exception=True,
            )

        assert isinstance(msg, SlackMessage)

    # TODO(lasuillard): Test `.prepare_message()`
    # TODO(lasuillard): Test `._make_inform_attachment()`

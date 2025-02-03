from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.messenger import Messenger
from django_slack_tools.slack_messages.middlewares import DjangoDatabasePersister, DjangoDatabasePolicyHandler
from django_slack_tools.slack_messages.models import SlackMessage
from django_slack_tools.slack_messages.models.messaging_policy import SlackMessagingPolicy
from django_slack_tools.slack_messages.request import MessageRequest
from django_slack_tools.slack_messages.response import MessageResponse
from tests._factories import SlackApiErrorFactory
from tests._helpers import AnyRegex
from tests.slack_messages._factories import (
    MessageRequestFactory,
    MessageResponseFactory,
    SlackGetPermalinkResponseFactory,
)
from tests.slack_messages.models._factories import (
    SlackMentionFactory,
    SlackMessageRecipientFactory,
    SlackMessagingPolicyFactory,
)

if TYPE_CHECKING:
    from slack_bolt import App

    from django_slack_tools.app_settings import SettingsDict


pytestmark = [
    pytest.mark.usefixtures("override_app_settings"),
    pytest.mark.django_db,
]


@pytest.fixture(scope="session")
def app_settings() -> SettingsDict:
    return {
        "slack_app": "testproj.config.slack_app.app",
        "messengers": {
            "test-django-middleware": {
                "class": "django_slack_tools.slack_messages.messenger.Messenger",
                "kwargs": {
                    "template_loaders": [
                        {
                            "class": "django_slack_tools.slack_messages.template_loaders.DjangoPolicyTemplateLoader",
                            "kwargs": {},
                        },
                    ],
                    "middlewares": [
                        {
                            "class": "django_slack_tools.slack_messages.middlewares.DjangoDatabasePersister",
                            "kwargs": {},
                        },
                    ],
                    "messaging_backend": {
                        "class": "django_slack_tools.slack_messages.backends.DummyBackend",
                        "kwargs": {},
                    },
                },
            },
        },
    }


class TestDjangoDatabasePersister:
    def test_instance_creation(self, slack_app: App) -> None:
        """Test various instance creation scenarios."""
        DjangoDatabasePersister(slack_app=None, get_permalink=False)
        with pytest.raises(
            ValueError,
            match="`slack_app` must be an instance of `App` if `get_permalink` is set `True`.",
        ):
            DjangoDatabasePersister(slack_app=None, get_permalink=True)

        DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)
        DjangoDatabasePersister(slack_app=slack_app, get_permalink=False)

    def test_process_response(self, slack_app: App, mock_slack_client: mock.Mock) -> None:
        """Test processing the response."""
        permalink = "https://example.com/permalink"
        mock_slack_client.chat_getPermalink.return_value = SlackGetPermalinkResponseFactory(permalink=permalink)
        persister = DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)

        response = MessageResponseFactory()
        result = persister.process_response(response)
        saved_message = SlackMessage.objects.get(id=response.request.id_)

        assert result is response
        assert saved_message.policy is None
        assert saved_message.channel == response.request.channel
        assert saved_message.header == {
            "mrkdwn": None,
            "parse": None,
            "reply_broadcast": None,
            "thread_ts": None,
            "unfurl_links": None,
            "unfurl_media": None,
        }
        assert saved_message.body == {}
        assert saved_message.ok == response.ok
        assert saved_message.permalink == permalink
        assert saved_message.ts == response.ts
        assert saved_message.parent_ts == ""
        assert MessageRequest.model_validate(saved_message.request)
        assert MessageResponse.model_validate(saved_message.response)
        assert saved_message.exception == ""

    def test_process_response_fail_save_db(self) -> None:
        """Test failing to save to the database. It should log the error, but not raise it."""
        persister = DjangoDatabasePersister()
        with mock.patch("django_slack_tools.slack_messages.models.SlackMessage.save") as mock_save:
            mock_save.side_effect = Exception("Some error occurred")
            persister.process_response(MessageResponseFactory())

    def test_process_response_skip_persist_if_request_none(self) -> None:
        """Test skipping persisting if `response.request` is `None`."""
        persister = DjangoDatabasePersister()

        response = MessageResponseFactory(request=None)
        result = persister.process_response(response)

        assert result is response
        assert not SlackMessage.objects.exists()

    def test_get_permalink(self, slack_app: App, mock_slack_client: mock.Mock) -> None:
        """Test getting permalink for the message."""
        expect = "https://example.com/permalink"
        mock_slack_client.chat_getPermalink.return_value = SlackGetPermalinkResponseFactory(permalink=expect)
        persister = DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)
        permalink = persister._get_permalink(channel="test-channel", ts="some-ts")
        assert permalink == expect

    def test_get_permalink_error_api_call_fails(self, slack_app: App, mock_slack_client: mock.Mock) -> None:
        """Test getting permalink error when API call fails."""
        mock_slack_client.chat_getPermalink.side_effect = SlackApiErrorFactory()
        persister = DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)
        permalink = persister._get_permalink(channel="test-channel", ts="some-ts")
        assert permalink == ""

    def test_get_permalink_error_no_slack_app(self, slack_app: App) -> None:
        """Test getting permalink error when slack_app is None."""
        persister = DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)
        persister.slack_app = None  # Bypass the validation in the constructor
        permalink = persister._get_permalink(channel="test-channel", ts="some-ts")
        assert permalink == ""

    def test_get_permalink_error_no_ts(self, slack_app: App) -> None:
        """Test getting permalink error when ts is empty."""
        persister = DjangoDatabasePersister(slack_app=slack_app, get_permalink=True)
        assert persister._get_permalink(channel="test-channel", ts="") == ""


class TestDjangoDatabasePolicyHandler:
    def test_instance_creation(self) -> None:
        """Test various instance creation scenarios."""
        messenger = Messenger(template_loaders=[], middlewares=[], messaging_backend=DummyBackend())

        middleware = DjangoDatabasePolicyHandler(messenger=messenger, auto_create_policy=False)
        assert middleware.messenger == messenger

        middleware = DjangoDatabasePolicyHandler(messenger=messenger, auto_create_policy=True)
        assert middleware.messenger == messenger

        middleware = DjangoDatabasePolicyHandler(messenger="test-django-middleware", auto_create_policy=False)
        assert isinstance(middleware.messenger, Messenger)

        middleware = DjangoDatabasePolicyHandler(messenger="test-django-middleware", auto_create_policy=True)
        assert isinstance(middleware.messenger, Messenger)

    def test_process_request(self) -> None:
        """Test processing the request."""
        # Arrange
        middleware = DjangoDatabasePolicyHandler(messenger="test-django-middleware")
        recipients = [SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(3)) for _ in range(3)]
        policy = SlackMessagingPolicyFactory(
            recipients=recipients,
            template_type=SlackMessagingPolicy.TemplateType.DJANGO_INLINE,
            template="""
<root>
    <block type="section">
        <text type="mrkdwn">
            {{ greet }}, {{ mentions | join:", " }}!
        </text>
    </block>
</root>
            """.strip(),
        )

        # Act
        # Original request will be stopped, and 3 new requests will be created
        response = middleware.process_request(
            MessageRequestFactory(
                channel=policy.code,
                context={"greet": "Nice to meet you"},
            ),
        )

        # Assert
        assert response is None
        assert SlackMessage.objects.count() == 3
        assert list(
            SlackMessage.objects.all().values("policy", "channel", "header", "body", "ok"),
        ) == [
            {
                "policy": None,
                "channel": mock.ANY,
                "header": {
                    "mrkdwn": None,
                    "parse": None,
                    "reply_broadcast": None,
                    "thread_ts": None,
                    "unfurl_links": None,
                    "unfurl_media": None,
                },
                "body": {
                    "attachments": None,
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": AnyRegex(r"Nice to meet you, .*, .*, .*!")},
                        },
                    ],
                    "text": None,
                    "icon_emoji": None,
                    "icon_url": None,
                    "metadata": None,
                    "username": None,
                },
                "ok": True,
            },
            {
                "policy": None,
                "channel": mock.ANY,
                "header": {
                    "mrkdwn": None,
                    "parse": None,
                    "reply_broadcast": None,
                    "thread_ts": None,
                    "unfurl_links": None,
                    "unfurl_media": None,
                },
                "body": {
                    "attachments": None,
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": AnyRegex(r"Nice to meet you, .*, .*, .*!")},
                        },
                    ],
                    "text": None,
                    "icon_emoji": None,
                    "icon_url": None,
                    "metadata": None,
                    "username": None,
                },
                "ok": True,
            },
            {
                "policy": None,
                "channel": mock.ANY,
                "header": {
                    "mrkdwn": None,
                    "parse": None,
                    "reply_broadcast": None,
                    "thread_ts": None,
                    "unfurl_links": None,
                    "unfurl_media": None,
                },
                "body": {
                    "attachments": None,
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": AnyRegex(r"Nice to meet you, .*, .*, .*!")},
                        },
                    ],
                    "text": None,
                    "icon_emoji": None,
                    "icon_url": None,
                    "metadata": None,
                    "username": None,
                },
                "ok": True,
            },
        ]

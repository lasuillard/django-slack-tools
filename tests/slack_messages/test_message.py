from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_bot.slack_messages.message import slack_message, slack_message_via_policy
from django_slack_bot.slack_messages.models import SlackMention, SlackMessage, SlackMessagingPolicy
from tests.slack_messages.models._factories import (
    SlackMentionFactory,
    SlackMessageRecipientFactory,
    SlackMessagingPolicyFactory,
)

from ._factories import SlackMessageResponseFactory

if TYPE_CHECKING:
    from unittest.mock import Mock

pytestmark = pytest.mark.django_db


def test_slack_message(mock_slack_client: Mock) -> None:
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
    msg = slack_message("Hello, World!", channel="whatever-channel")

    assert isinstance(msg, SlackMessage)
    assert SlackMessage.objects.filter(id=msg.id).exists()
    assert msg.policy is None
    assert msg.channel == "whatever-channel"
    assert msg.header == {}
    assert msg.body["text"] == "Hello, World!"
    assert msg.ok
    assert msg.permalink == ""
    assert msg.ts
    assert msg.parent_ts == ""
    assert isinstance(msg.request, dict)
    assert isinstance(msg.response, dict)
    assert msg.exception == ""


def test_slack_message_via_policy(mock_slack_client: Mock) -> None:
    recipients = [
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(
            mentions=[SlackMentionFactory(type=SlackMention.MentionType.SPECIAL, mention_id="<!here>")],
        ),
    ]
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-001",
        template={
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "{greet}, {mentions}",
                    },
                },
            ],
        },
        recipients=recipients,
    )
    mock_slack_client.chat_postMessage.side_effect = SlackMessageResponseFactory.create_batch(size=3)
    messages = slack_message_via_policy(policy, context={"greet": "Nice to meet you"})

    assert len(messages) == 3
    assert all(isinstance(msg, SlackMessage) for msg in messages)
    ids = [msg.id for msg in messages]  # type: ignore[union-attr]
    assert SlackMessage.objects.filter(id__in=ids).count() == 3


def test_slack_message_via_policy_policy_not_enabled(mock_slack_client: Mock) -> None:
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-002",
        enabled=False,
        recipients=[
            SlackMessageRecipientFactory(),
        ],
    )
    messages = slack_message_via_policy(policy.code, context={"greet": "Nice to meet you"})
    mock_slack_client.chat_postMessage.assert_not_called()

    assert messages == []


def test_slack_message_via_policy_context_shadowing_defaults(mock_slack_client: Mock) -> None:
    """Test template kwargs being shadowed by user provided context."""
    policy = SlackMessagingPolicyFactory(code="TEST", recipients=[])

    # As there is no recipient, no message will be sent
    # It's just OK no exception being thrown
    messages = slack_message_via_policy(policy.code, context={"mentions_as_str": "💣"})
    mock_slack_client.chat_postMessage.assert_not_called()

    assert messages == []


def test_slack_message_via_policy_lazy(mock_slack_client: Mock) -> None:
    # Policy not exist at first
    code = "TEST-PO-LAZY-001"
    assert not SlackMessagingPolicy.objects.filter(code=code).exists()

    # Make call with lazy mode
    messages = slack_message_via_policy(code, lazy=True, context={"message": "Nice to meet you"})
    mock_slack_client.chat_postMessage.assert_not_called()

    # Ensure policy has been created
    policy = SlackMessagingPolicy.objects.get(code=code)
    assert policy.code == code
    assert policy.enabled is False
    assert not policy.recipients.exists()
    assert policy.template is None

    # No message will be sent
    assert len(messages) == 0

    # Update policy
    policy.enabled = True
    policy.template = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "{message}, {mentions_as_str}",
                },
            },
        ],
    }
    policy.save()
    policy.recipients.add(
        SlackMessageRecipientFactory(
            channel="whatever-channel",
            mentions=[SlackMentionFactory(type=SlackMention.MentionType.SPECIAL, mention_id="<!channel>")],
        ),
    )

    # Re-send message
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
    messages = slack_message_via_policy(code, lazy=True, context={"message": "Nice to meet you"})

    assert len(messages) == 1
    message = messages.pop()
    assert isinstance(message, SlackMessage)
    assert message.policy == policy
    assert message.channel == "whatever-channel"
    assert message.body["blocks"] == [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Nice to meet you, <!channel>",
            },
        },
    ]
    assert message.ok is True
    assert message.ts

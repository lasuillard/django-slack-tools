from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_tools.slack_messages.message import slack_message, slack_message_via_policy
from django_slack_tools.slack_messages.models import SlackMention, SlackMessage, SlackMessagingPolicy
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


def test_slack_message_via_policy_dict_template(mock_slack_client: Mock) -> None:
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
    num_sent = slack_message_via_policy(policy, context={"greet": "Nice to meet you"})

    assert num_sent == 3
    assert SlackMessage.objects.filter(policy=policy).count() == 3


def test_slack_message_via_policy_django_template(mock_slack_client: Mock) -> None:
    recipients = [
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(
            mentions=[SlackMentionFactory(type=SlackMention.MentionType.SPECIAL, mention_id="<!here>")],
        ),
    ]
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-001-DJ",
        template_type=SlackMessagingPolicy.TemplateType.Django,
        template="greet.xml",
        recipients=recipients,
    )
    mock_slack_client.chat_postMessage.side_effect = SlackMessageResponseFactory.create_batch(size=3)
    num_sent = slack_message_via_policy(policy, context={"greet": "Nice to meet you"})

    assert num_sent == 3
    assert SlackMessage.objects.filter(policy=policy).count() == 3


def test_slack_message_via_policy_django_inline_template(mock_slack_client: Mock) -> None:
    recipients = [
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(
            mentions=[SlackMentionFactory(type=SlackMention.MentionType.SPECIAL, mention_id="<!here>")],
        ),
    ]
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-001-DJI",
        template_type=SlackMessagingPolicy.TemplateType.DjangoInline,
        template="""
            <root>
                <block type="section">
                    <text type="mrkdwn">
                        {{ greet }}, {{ mentions }}
                    </text>
                </block>
            </root>
        """,
        recipients=recipients,
    )
    mock_slack_client.chat_postMessage.side_effect = SlackMessageResponseFactory.create_batch(size=3)
    num_sent = slack_message_via_policy(policy, context={"greet": "Nice to meet you"})

    assert num_sent == 3
    assert SlackMessage.objects.filter(policy=policy).count() == 3


def test_slack_message_via_policy_unknown_template_type(mock_slack_client: Mock) -> None:
    recipients = [
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
    ]
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-001-?",
        template_type=SlackMessagingPolicy.TemplateType.UNKNOWN,
        template=None,
        recipients=recipients,
    )
    mock_slack_client.chat_postMessage.side_effect = [SlackMessageResponseFactory()]
    with pytest.raises(ValueError, match="Unsupported template type: SlackMessagingPolicy.TemplateType.UNKNOWN"):
        slack_message_via_policy(policy, context={"greet": "Nice to meet you"})


def test_slack_message_via_policy_default(mock_slack_client: Mock) -> None:
    default_policy = SlackMessagingPolicy.objects.get(code="DEFAULT")
    default_policy.enabled = True
    default_policy.template = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "{greet}, {mentions_as_str}",
                },
            },
        ],
    }
    default_policy.save()
    default_policy.recipients.add(
        SlackMessageRecipientFactory(
            channel="whatever-channel",
            mentions=[SlackMentionFactory(type=SlackMention.MentionType.SPECIAL, mention_id="<!channel>")],
        ),
    )

    mock_slack_client.chat_postMessage.side_effect = SlackMessageResponseFactory()
    num_sent = slack_message_via_policy(context={"greet": "Nice to meet you"})

    assert num_sent == 1
    assert SlackMessage.objects.filter(policy=default_policy).count() == 1


def test_slack_message_via_policy_policy_not_enabled(mock_slack_client: Mock) -> None:
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-002",
        enabled=False,
        recipients=[
            SlackMessageRecipientFactory(),
        ],
    )
    num_sent = slack_message_via_policy(policy.code, context={"greet": "Nice to meet you"})
    mock_slack_client.chat_postMessage.assert_not_called()

    assert num_sent == 0


def test_slack_message_via_policy_context_shadowing_defaults(mock_slack_client: Mock) -> None:
    """Test template kwargs being shadowed by user provided context."""
    policy = SlackMessagingPolicyFactory(code="TEST", recipients=[])

    # As there is no recipient, no message will be sent
    # It's just OK no exception being thrown
    num_sent = slack_message_via_policy(policy.code, context={"mentions_as_str": "💣"})
    mock_slack_client.chat_postMessage.assert_not_called()

    assert num_sent == 0


def test_slack_message_via_policy_lazy(mock_slack_client: Mock) -> None:
    # Policy not exist at first
    code = "TEST-PO-LAZY-001"
    assert not SlackMessagingPolicy.objects.filter(code=code).exists()

    # Make call with lazy mode
    num_sent = slack_message_via_policy(code, lazy=True, context={"message": "Nice to meet you"})
    mock_slack_client.chat_postMessage.assert_not_called()

    # Ensure policy has been created
    policy = SlackMessagingPolicy.objects.get(code=code)
    assert policy.code == code
    assert policy.enabled is False
    assert list(policy.recipients.values_list("alias", flat=True)) == ["DEFAULT"]
    assert policy.template == {"text": "No template configured for lazily created policy {policy}"}

    # No message will be sent
    assert num_sent == 0


def test_slack_message_via_policy_lazy_already_exists(mock_slack_client: Mock) -> None:
    policy = SlackMessagingPolicyFactory(
        code="TEST-PO-LAZY-002",
        enabled=True,
        recipients=[
            SlackMessageRecipientFactory(),
        ],
    )

    # Make call with lazy mode
    mock_slack_client.chat_postMessage.return_value = SlackMessageResponseFactory()
    num_sent = slack_message_via_policy(policy.code, lazy=True, context={"message": "Nice to meet you"})

    # No message will be sent
    assert num_sent == 1

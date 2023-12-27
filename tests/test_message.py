from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_bot.message import slack_message, slack_message_via_policy
from django_slack_bot.models import SlackMessage
from tests.models._factories import SlackMentionFactory, SlackMessageRecipientFactory, SlackMessagingPolicyFactory

if TYPE_CHECKING:
    from django_slack_bot.backends import SlackRedirectBackend


@pytest.mark.vcr()
@pytest.mark.django_db()
def test_slack_message(slack_redirect_backend: SlackRedirectBackend) -> None:  # noqa: ARG001
    msg = slack_message("Hello, World!", channel="whatever-channel")
    assert isinstance(msg, SlackMessage)
    msg_from_db = SlackMessage.objects.get(id=msg.id)
    assert msg_from_db.body["text"] == "Hello, World!"
    assert msg_from_db.ok


@pytest.mark.vcr()
@pytest.mark.django_db()
def test_slack_message_via_policy(slack_redirect_backend: SlackRedirectBackend) -> None:  # noqa: ARG001
    recipients = [
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(mentions=SlackMentionFactory.create_batch(size=2)),
        SlackMessageRecipientFactory(mentions=[SlackMentionFactory(mention="<!here>")]),
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

    messages = slack_message_via_policy(policy.code, greet="Nice to meet you")
    assert len(messages) == 3
    assert all(isinstance(msg, SlackMessage) for msg in messages)

    ids = [msg.id for msg in messages]  # type: ignore[union-attr]
    assert SlackMessage.objects.filter(id__in=ids).count() == 3

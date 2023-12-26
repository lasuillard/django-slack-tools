from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_slack_bot.message import slack_message
from django_slack_bot.models import SlackMessage

if TYPE_CHECKING:
    from django_slack_bot.backends import SlackRedirectBackend


@pytest.mark.vcr()
@pytest.mark.django_db()
def test_slack_message(slack_redirect_backend: SlackRedirectBackend) -> None:  # noqa: ARG001
    msg = slack_message("Hello, World!", channel="D069G3W44SY")
    assert isinstance(msg, SlackMessage)
    msg_from_db = SlackMessage.objects.get(id=msg.id)
    assert msg_from_db.body["text"] == "Hello, World!"
    assert msg_from_db.ok

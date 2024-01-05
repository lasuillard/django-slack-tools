from __future__ import annotations

from typing import Any

import pytest

from django_slack_bot.choices import MentionType
from django_slack_bot.models import SlackMention

from ._factories import SlackMentionFactory
from ._helpers import ModelTestBase


class TestSlackMention(ModelTestBase):
    model_cls = SlackMention
    factory_cls = SlackMentionFactory

    @pytest.mark.parametrize(
        argnames=["kwargs", "expect"],
        argvalues=[
            [
                {"type": MentionType.SPECIAL, "name": "Here", "mention": "<!here>"},
                "Here (<!here>, Special)",
            ],
            [
                {"type": MentionType.USER, "name": "lasuillard", "mention": "<@U0000000000>"},
                "lasuillard (<@U0000000000>, User)",
            ],
            [
                {"type": MentionType.GROUP, "name": "Backend", "mention": "<subteam^T0000000000>"},
                "Backend (<subteam^T0000000000>, Group)",
            ],
        ],
        ids=["special mention", "user mention", "team mention"],
    )
    def test_str(self, kwargs: dict[str, Any], expect: str) -> None:
        instance = self.factory_cls.build(**kwargs)
        assert str(instance) == expect

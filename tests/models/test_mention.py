from __future__ import annotations

from typing import Any

import pytest

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
                {"type": SlackMention.MentionType.SPECIAL, "name": "Here", "mention_id": "<!here>"},
                "Here (Special, <!here>)",
            ],
            [
                {"type": SlackMention.MentionType.USER, "name": "lasuillard", "mention_id": "U0000000000"},
                "lasuillard (User, U0000000000)",
            ],
            [
                {"type": SlackMention.MentionType.GROUP, "name": "Backend", "mention_id": "T0000000000"},
                "Backend (Group, T0000000000)",
            ],
        ],
        ids=["special", "user", "team"],
    )
    def test_str(self, kwargs: dict[str, Any], expect: str) -> None:
        instance = self.factory_cls.build(**kwargs)
        assert str(instance) == expect

    @pytest.mark.parametrize(
        argnames=["kwargs", "expect"],
        argvalues=[
            [
                {"type": SlackMention.MentionType.SPECIAL, "name": "Here", "mention_id": "<!here>"},
                "<!here>",
            ],
            [
                {"type": SlackMention.MentionType.USER, "name": "lasuillard", "mention_id": "U0000000000"},
                "<@U0000000000>",
            ],
            [
                {"type": SlackMention.MentionType.GROUP, "name": "Backend", "mention_id": "T0000000000"},
                "<!subteam^T0000000000>",
            ],
        ],
        ids=["special", "user", "team"],
    )
    def test_mention(self, kwargs: dict[str, Any], expect: str) -> None:
        instance = self.factory_cls.build(**kwargs)
        assert instance.mention == expect

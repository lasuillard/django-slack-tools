from __future__ import annotations

from typing import Any

import pytest

from django_slack_bot.models import SlackMessage
from tests._helpers import ModelTestBase

from ._factories import SlackMessageFactory


class TestSlackMessage(ModelTestBase):
    model_cls = SlackMessage
    factory_cls = SlackMessageFactory

    @pytest.mark.parametrize(
        argnames=["kwargs", "expect"],
        argvalues=[
            [{"ts": "1703393199.592689", "ok": True}, "Message (1703393199.592689, OK)"],
            [{"id": 1, "ok": False}, "Message (1, not OK)"],
            [{"id": 2, "ok": None}, "Message (2, not sent)"],
        ],
        ids=["ok", "not ok", "not sent"],
    )
    def test_str(self, kwargs: dict[str, Any], expect: str) -> None:
        instance = self.factory_cls.build(**kwargs)
        assert str(instance) == expect

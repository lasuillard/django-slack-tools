import pytest

from django_slack_bot.models import SlackMessageRecipient
from tests._helpers import ModelTestBase

from ._factories import SlackMentionFactory, SlackMessageRecipientFactory


class TestSlackMessageRecipient(ModelTestBase):
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory

    @pytest.mark.django_db()
    def test_str(self) -> None:
        instance = self.factory_cls(
            alias="Robots in the bar",
            channel="#robots-in-the-bar",
            mentions=SlackMentionFactory.create_batch(size=3),
        )
        assert str(instance) == "Robots in the bar (#robots-in-the-bar, 3 mentions)"

import pytest

from django_slack_bot.slack_messages.models import SlackMessageRecipient

from ._factories import SlackMentionFactory, SlackMessageRecipientFactory
from ._helpers import ModelTestBase


class TestSlackMessageRecipient(ModelTestBase):
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory

    @pytest.mark.django_db()
    def test_str(self) -> None:
        instance = self.factory_cls.create(
            alias="Robots in the bar",
            channel="#robots-in-the-bar",
            mentions=SlackMentionFactory.create_batch(size=3),
        )
        assert str(instance) == "Robots in the bar (#robots-in-the-bar, 3 mentions)"

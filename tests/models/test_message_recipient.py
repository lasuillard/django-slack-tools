from django_slack_bot.models import SlackMessageRecipient
from tests._helpers import ModelTestBase

from ._factories import SlackMessageRecipientFactory


class TestSlackMessageRecipient(ModelTestBase):
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory

    def test_str(self) -> None:
        instance = self.factory_cls.build(
            alias="Robots in the bar",
            channel="#robots-in-the-bar",
            mentions=["@dancing-bot", "@coding-bot", "@polling-bot"],
        )
        assert str(instance) == "Robots in the bar (#robots-in-the-bar, 3 mentions)"

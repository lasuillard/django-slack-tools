from django_slack_tools.slack_messages.models import SlackMessagingPolicy
from tests._helpers import ModelTestBase

from ._factories import SlackMessageRecipientFactory, SlackMessagingPolicyFactory


class TestSlackMessagingPolicy(ModelTestBase):
    model_cls = SlackMessagingPolicy
    factory_cls = SlackMessagingPolicyFactory

    def test_str(self) -> None:
        # Enabled with recipients
        recipients = SlackMessageRecipientFactory.create_batch(size=3)
        instance = self.factory_cls.create(code="OP-641-XA01", enabled=True, recipients=recipients)
        assert str(instance) == "OP-641-XA01 (enabled, 3 recipients)"

        # Disabled but existing recipients
        recipients = SlackMessageRecipientFactory.create_batch(size=1)
        instance = self.factory_cls.create(code="REPORT-1178-CR9217", enabled=False, recipients=recipients)
        assert str(instance) == "REPORT-1178-CR9217 (disabled, 1 recipients)"

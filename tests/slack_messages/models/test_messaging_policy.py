import pytest

from django_slack_bot.slack_messages.models import SlackMessagingPolicy

from ._factories import SlackMessageRecipientFactory, SlackMessagingPolicyFactory
from ._helpers import ModelTestBase


class TestSlackMessagingPolicy(ModelTestBase):
    model_cls = SlackMessagingPolicy
    factory_cls = SlackMessagingPolicyFactory

    @pytest.mark.django_db()  # Exit with max recursion error w/o this
    def test_str(self) -> None:
        # Enabled with recipients
        recipients = SlackMessageRecipientFactory.create_batch(size=3)
        instance = self.factory_cls.create(code="OP-641-XA01", enabled=True, recipients=recipients)
        assert str(instance) == "OP-641-XA01 (enabled, 3 recipients)"

        # Disabled but existing recipients
        recipients = SlackMessageRecipientFactory.create_batch(size=1)
        instance = self.factory_cls.create(code="REPORT-1178-CR9217", enabled=False, recipients=recipients)
        assert str(instance) == "REPORT-1178-CR9217 (disabled, 1 recipients)"

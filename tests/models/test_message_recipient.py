from django_slack_bot.models import SlackMessageRecipient
from tests._helpers import ModelTestBase

from ._factories import SlackMessageRecipientFactory


class SlackMessageRecipientTests(ModelTestBase):
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory

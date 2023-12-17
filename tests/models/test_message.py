from django_slack_bot.models import SlackMessage
from tests._helpers import ModelTestBase

from ._factories import SlackMessageFactory


class SlackMessageTests(ModelTestBase):
    model_cls = SlackMessage
    factory_cls = SlackMessageFactory

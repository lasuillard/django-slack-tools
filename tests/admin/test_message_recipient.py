from django_slack_bot.admin import SlackMessageRecipientAdmin
from django_slack_bot.models import SlackMessageRecipient
from tests._helpers import ModelAdminTestBase
from tests.models._factories import SlackMessageRecipientFactory


class SlackMessageRecipientAdminTests(ModelAdminTestBase):
    admin_cls = SlackMessageRecipientAdmin
    model_cls = SlackMessageRecipient
    factory_cls = SlackMessageRecipientFactory

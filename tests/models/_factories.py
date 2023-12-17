from typing import Any, ClassVar, Sequence

import faker
from django.utils import timezone
from factory import Faker, LazyAttribute, post_generation
from factory.django import DjangoModelFactory

from django_slack_bot.models import SlackMessage, SlackMessageRecipient, SlackMessagingPolicy

_fake = faker.Faker()


class SlackMessageRecipientFactory(DjangoModelFactory):
    class Meta:
        model = SlackMessageRecipient

    alias = Faker("name")
    channel = LazyAttribute(lambda _: f"#{_fake.pystr()}")
    mentions = LazyAttribute(
        # This is CSV field
        lambda _: [_fake.pystr() for _ in range(3)],
    )


class SlackMessageFactory(DjangoModelFactory):
    class Meta:
        model = SlackMessage

    policy = None
    channel = LazyAttribute(lambda _: f"#{_fake.pystr()}")
    body = LazyAttribute(lambda o: {"channel": o.channel, "text": _fake.paragraph()})
    ok = True
    ts = LazyAttribute(lambda _: str(timezone.now().timestamp()))
    parent_ts = ""
    request = None
    response = None


class SlackMessagingPolicyFactory(DjangoModelFactory):
    class Meta:
        model = SlackMessagingPolicy

    code = Faker("pystr")
    enabled = True

    @post_generation
    def recipients(
        self: SlackMessagingPolicy,
        create: bool,  # noqa: FBT001
        extracted: Sequence[SlackMessageRecipient],
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        if not create or not extracted:
            return

        self.recipients.add(*extracted)

    template: ClassVar = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello, World!: {mentions}",
                },
            },
        ],
    }

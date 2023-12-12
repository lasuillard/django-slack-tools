from django.conf import settings
from slack_bolt import App


def get_slack_app() -> App:  # noqa: D103
    return App(
        token=settings.SLACK_BOT_TOKEN,
        signing_secret=settings.SLACK_SIGNING_SECRET,
    )

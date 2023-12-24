from django.conf import settings
from slack_bolt import App

app = App(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
    token_verification_enabled=False,  # Not to bother dev tasks
)

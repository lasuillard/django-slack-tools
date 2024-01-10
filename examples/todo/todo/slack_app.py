from django.conf import settings
from slack_bolt import App

app = App(token=settings.SLACK_BOT_TOKEN, signing_secret=settings.SLACK_SIGNING_SECRET)

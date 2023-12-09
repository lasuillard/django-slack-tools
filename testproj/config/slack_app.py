import os

from slack_bolt import App

# TODO(lasuillard): Move env loading to settings
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)

import logging

from slack_bolt.context.say import Say

from todo_bot.slack_app import app

logger = logging.getLogger(__name__)


@app.event("app_mention")
def handle_app_mention(event: dict, say: Say) -> None:
    """Handles `app_mention` event. This requires `app_mentions:read` scope."""
    logger.info("Received an event: %r", event)
    say(f"Hi there, <@{event['user']}>!")

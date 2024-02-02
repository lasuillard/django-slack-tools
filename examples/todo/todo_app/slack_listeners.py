from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from todo.slack_app import app

from .models import Todo

if TYPE_CHECKING:
    from slack_bolt.context.ack import Ack
    from slack_bolt.context.say import Say
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)


# App home
# https://api.slack.com/start/building/bolt-python
@app.event("app_home_opened")
def update_home_tab(client: WebClient, event: dict) -> None:
    """Show the user's To Do list when App Home is opened."""
    recent_todos = Todo.objects.filter(completed=False).order_by("-last_modified")[:5]  # type: ignore[attr-defined]
    recent_todo_element = {
        "type": "rich_text",
        "elements": [
            {
                "type": "rich_text_list",
                "style": "bullet",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": f"{todo.title}\n",
                                "style": {
                                    "bold": True,
                                },
                            },
                            {
                                "type": "text",
                                "text": "{description}\n".format(
                                    description=todo.description or "No description",
                                ),
                            },
                            {
                                "type": "text",
                                "text": f"Created in {todo.created:%Y-%m-%d}",
                            },
                        ],
                    }
                    for todo in recent_todos
                ],
            },
        ],
    }
    client.views_publish(
        user_id=event["user"],
        view={
            "type": "home",
            "callback_id": "home_view",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome to Django Slack Tools :tada:",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a sample Slack app built with <https://slack.dev/bolt-python/tutorial/getting-started|Bolt for Python> to display a list of To Do.",  # noqa: E501
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"There is {len(recent_todos)} To Do not completed yet.",
                    },
                },
                recent_todo_element,
            ],
        },
    )


@app.shortcut("create_todo")
def create_todo(
    ack: Ack,
    client: WebClient,
    body: dict,
) -> None:
    """Shortcut to create a new To Do."""
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "create_todo",
            "title": {"type": "plain_text", "text": "Create new To Do", "emoji": True},
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
            "blocks": [
                {
                    "block_id": "title",
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action",
                    },
                    "label": {"type": "plain_text", "text": "Title", "emoji": True},
                },
                {
                    "block_id": "description",
                    "type": "input",
                    "optional": True,
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "plain_text_input-action",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Description",
                        "emoji": True,
                    },
                },
            ],
        },
    )


@app.view("create_todo")
def handle_submission_create_todo(ack: Ack, body: dict) -> None:
    """Handle submission of a new To Do."""
    ack()
    values = body["view"]["state"]["values"]
    Todo.objects.create(  # type: ignore[attr-defined]
        title=values["title"]["plain_text_input-action"]["value"],
        description=values["description"]["plain_text_input-action"]["value"] or "",
    )


@app.shortcut("mark_todo_completed")
def mark_todo_completed(
    ack: Ack,
    client: WebClient,
    body: dict,
) -> None:
    """Shortcut to mark a To Do as completed."""
    logger.info("Received a body: %r", body)
    ack()
    incomplete_todos = Todo.objects.filter(completed=False).order_by("-last_modified")  # type: ignore[attr-defined]
    options = [
        {
            "text": {
                "type": "plain_text",
                "text": todo.title,
                "emoji": True,
            },
            "value": str(todo.id),
        }
        for todo in incomplete_todos
    ]
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "mark_todo_completed",
            "title": {"type": "plain_text", "text": "Create new To Do", "emoji": True},
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
            "blocks": [
                {
                    "block_id": "choice",
                    "type": "input",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True,
                        },
                        "options": options,
                        "action_id": "static_select-action",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Completed To Do",
                        "emoji": True,
                    },
                },
            ],
        },
    )


@app.view("mark_todo_completed")
def handle_submission_mark_todo_completed(ack: Ack, body: dict) -> None:
    """Handle submission of a new To Do."""
    ack()
    id_ = body["view"]["state"]["values"]["choice"]["static_select-action"]["selected_option"]["value"]
    todo = Todo.objects.get(id=id_)  # type: ignore[attr-defined]
    todo.completed = True
    todo.save()


@app.event("app_mention")
def handle_app_mention(event: dict, say: Say) -> None:
    """Reply greet to user."""
    logger.info("Received an event: %r", event)
    say(f"Hi there, <@{event['user']}>!")

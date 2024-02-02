from django_slack_bot.slack_messages.message import slack_message_via_policy

from .models import Todo


def create_todo(title: str, description: str) -> Todo:
    """Create a new To Do."""
    todo = Todo.objects.create(title=title, description=description)  # type: ignore[attr-defined]
    slack_message_via_policy("TODO-CREATED", lazy=True, context={"title": todo.title})
    return todo  # type:ignore[no-any-return]


def mark_todo_as_completed(todo_id: int) -> None:
    """Mark a To Do as completed."""
    todo = Todo.objects.get(id=todo_id)  # type: ignore[attr-defined]
    todo.completed = True
    todo.save()
    slack_message_via_policy("TODO-COMPLETED", lazy=True, context={"title": todo.title})

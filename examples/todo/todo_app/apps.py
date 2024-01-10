from django.apps import AppConfig


class TodoAppConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "todo_app"

    def ready(self) -> None:  # noqa: D102
        from . import slack_listeners  # noqa: F401

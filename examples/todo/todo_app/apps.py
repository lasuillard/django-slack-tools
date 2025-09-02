from django.apps import AppConfig


class TodoAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "todo_app"

    def ready(self) -> None:  # noqa: D102
        from . import signals, slack_listeners  # noqa: F401, PLC0415

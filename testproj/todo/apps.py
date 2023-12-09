from django.apps import AppConfig


class TodoConfig(AppConfig):  # noqa: D101
    name = "todo"

    def ready(self) -> None:  # noqa: D102
        from . import slack_listeners  # noqa: F401

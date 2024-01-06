"""Some helpful views."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse
    from slack_bolt import App


class SlackEventHandlerView(View):
    """View for handling Slack events."""

    app: App | None = None

    def __init__(self, *, app: App | Callable[[], App]) -> None:
        """Initialize view.

        Args:
            app: Slack app instance or callable which returns app.
        """
        if callable(app):
            app = app()

        self._event_handler = SlackRequestHandler(app=app)

        super().__init__()

    # Checking CSRF is nonsense because events come from Slack
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # noqa: D102, ARG002
        return self._event_handler.handle(request)

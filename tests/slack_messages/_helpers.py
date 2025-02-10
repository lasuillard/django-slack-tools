from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from django_slack_tools.slack_messages.backends import DummyBackend
from django_slack_tools.slack_messages.message_templates import BaseTemplate, PythonTemplate
from django_slack_tools.slack_messages.middlewares import (
    BaseMiddleware,
)
from django_slack_tools.slack_messages.template_loaders import (
    BaseTemplateLoader,
)

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.request import MessageRequest
    from django_slack_tools.slack_messages.response import MessageResponse


class MockTemplate(BaseTemplate):
    def __init__(self, render: Callable[[dict[str, Any]], Any]) -> None:
        self._render = render

    def render(self, context: dict[str, Any]) -> Any:
        return self._render(context)


class MockTemplateLoader(BaseTemplateLoader):
    def __init__(self, template: Any = None, *, key: str | None = None) -> None:
        self.template = template or PythonTemplate({"text": "Hello, {name}!"})
        self.key = key

    def load(self, key: str) -> PythonTemplate | None:
        if self.key and key != self.key:
            return None

        return self.template


class MockMiddleware(BaseMiddleware):
    def __init__(
        self,
        *,
        process_request: Callable[[MessageRequest], MessageRequest | None] | None = None,
        process_response: Callable[[MessageResponse], MessageResponse | None] | None = None,
    ) -> None:
        self._process_request = process_request
        self._process_response = process_response

    def process_request(self, request: MessageRequest) -> MessageRequest | None:
        if self._process_request:
            return self._process_request(request)

        return super().process_request(request)

    def process_response(self, response: MessageResponse) -> MessageResponse | None:
        if self._process_response:
            return self._process_response(response)

        return super().process_response(response)


class MockBackend(DummyBackend):
    def __init__(self, *, should_error: bool = False) -> None:
        self.should_error = should_error

    def _send_message(self, *args: Any, **kwargs: Any) -> Any:
        if self.should_error:
            msg = "Some error occurred"
            raise Exception(msg)  # noqa: TRY002

        return super()._send_message(*args, **kwargs)

from __future__ import annotations  # noqa: D100

import logging
from typing import TYPE_CHECKING, Any

from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest
from django_slack_tools.slack_messages.template_loaders import TemplateNotFoundError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django_slack_tools.slack_messages.backends import BaseBackend
    from django_slack_tools.slack_messages.message_templates import BaseTemplate
    from django_slack_tools.slack_messages.middlewares import BaseMiddleware
    from django_slack_tools.slack_messages.response import MessageResponse
    from django_slack_tools.slack_messages.template_loaders import BaseTemplateLoader

logger = logging.getLogger(__name__)

# TODO(lasuillard): Make logs more readable; list representation with `__str__()` instead of `__repr__()`


class Messenger:
    """Messenger class that sends message using templates and middlewares.

    Components evaluated in order:

    1. Request processing middlewares
    2. Load template by key and render message in-place
    4. Send message
    5. Response processing middlewares (in reverse order)
    """

    def __init__(
        self,
        *,
        template_loaders: Sequence[BaseTemplateLoader],
        middlewares: Sequence[BaseMiddleware],
        messaging_backend: BaseBackend,
    ) -> None:
        """Initialize the Messenger.

        Args:
            template_loaders: A sequence of template loaders.
                It is tried in order to load the template and the first one that returns a template is used.
            middlewares: A sequence of middlewares.
                Middlewares are applied in the order they are provided for request, and in reverse order for response.
            messaging_backend: The messaging backend to be used.
        """
        self.template_loaders = template_loaders
        self.middlewares = middlewares
        self.messaging_backend = messaging_backend
        logger.info(
            """Initialized messenger with: template loaders: %s, middlewares: %s, and messaging backend: %s""",
            template_loaders,
            middlewares,
            messaging_backend,
        )

    def send(
        self,
        to: str,
        *,
        template: str,
        context: dict[str, str],
        header: MessageHeader | dict[str, Any] | None = None,
    ) -> MessageResponse | None:
        """Shortcut of `.send_request()`."""
        header = MessageHeader.from_any(header or {})
        request = MessageRequest(template_key=template, channel=to, context=context, header=header)
        response = self.send_request(request=request)
        if response is None:
            return None

        return response

    def send_request(self, request: MessageRequest) -> MessageResponse | None:
        """Sends a message request and processes the response."""
        logger.info("Sending request: %s", request)
        _request = self._process_request(request)
        if _request is None:
            return None

        _request = self._render_message(_request)
        response = self._deliver_message(_request)
        _response = self._process_response(response)
        if _response is None:
            return None

        logger.info("Response: %s", _response)
        return response

    def _process_request(self, request: MessageRequest) -> MessageRequest | None:
        for middleware in self.middlewares:
            logger.debug("Processing request (%s) with middleware %s", request, middleware)
            new_request = middleware.process_request(request)
            if new_request is None:
                logger.warning("Middleware %s returned `None`, skipping remaining middlewares", middleware)
                return None

            request = new_request

        logger.debug("Request after processing: %s", request)
        return request

    def _render_message(self, request: MessageRequest) -> MessageRequest:
        template = self._get_template(request.template_key)
        logger.debug("Rendering request %s with template: %s", request, template)
        rendered = template.render(request.context)
        body = MessageBody.from_any(rendered)
        return request.copy_with_overrides(body=body)

    def _get_template(self, key: str) -> BaseTemplate:
        for loader in self.template_loaders:
            template = loader.load(key)
            if template is not None:
                return template

        msg = f"Template with key '{key}' not found"
        raise TemplateNotFoundError(msg)

    def _deliver_message(self, request: MessageRequest) -> MessageResponse:
        logger.debug("Delivering message request: %s", request)
        response = self.messaging_backend.deliver(request)
        logger.debug("Response after delivery: %s", response)
        return response

    def _process_response(self, response: MessageResponse) -> MessageResponse | None:
        for middleware in reversed(self.middlewares):
            logger.debug("Processing response (%s) with middleware: %s", response, middleware)
            new_response = middleware.process_response(response)
            if new_response is None:
                logger.warning("Middleware %s returned `None`, skipping remaining middlewares", middleware)
                return None

            response = new_response

        logger.debug("Response after processing: %s", response)
        return response

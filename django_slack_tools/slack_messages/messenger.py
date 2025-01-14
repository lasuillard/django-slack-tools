# noqa: D100
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django_slack_tools.slack_messages.backends import BaseBackend
from django_slack_tools.slack_messages.middlewares import BaseMiddleware
from django_slack_tools.slack_messages.request import MessageBody, MessageHeader, MessageRequest
from django_slack_tools.slack_messages.template_loaders import BaseTemplateLoader, TemplateNotFoundError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django_slack_tools.slack_messages.message_templates import BaseTemplate
    from django_slack_tools.slack_messages.response import MessageResponse

logger = logging.getLogger(__name__)


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
        # Validate the template loaders
        for tl in template_loaders:
            if not isinstance(tl, BaseTemplateLoader):
                msg = f"Expected inherited from {BaseTemplateLoader!s}, got {type(tl)}"
                raise TypeError(msg)

        self.template_loaders = template_loaders

        # Validate the middlewares
        for mw in middlewares:
            if not isinstance(mw, BaseMiddleware):
                msg = f"Expected inherited from {BaseMiddleware!s}, got {type(mw)}"
                raise TypeError(msg)

        self.middlewares = middlewares

        # Validate the messaging backend
        if not isinstance(messaging_backend, BaseBackend):
            msg = f"Expected inherited from {BaseBackend!s}, got {type(messaging_backend)}"
            raise TypeError(msg)

        self.messaging_backend = messaging_backend

        # Summary
        logger.info(
            (
                "Initialized messenger with:"
                "\n- Template loaders: %s"
                "\n- Middlewares: %s"
                "\n- Messaging backend: %s"
            ),
            ", ".join(cls.__class__.__name__ for cls in template_loaders),
            ", ".join(cls.__class__.__name__ for cls in middlewares),
            messaging_backend.__class__.__name__,
        )

    def send(
        self,
        to: str,
        *,
        template: str | None = None,
        context: dict[str, str],
        header: MessageHeader | dict[str, Any] | None = None,
    ) -> MessageResponse | None:
        """Simplified shortcut for `.send_request()`."""
        header = MessageHeader.model_validate(header or {})
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

        self._render_message(_request)
        response = self._deliver_message(_request)
        _response = self._process_response(response)
        if _response is None:
            return None

        logger.info("Response: %s", _response)
        return response

    def _process_request(self, request: MessageRequest) -> MessageRequest | None:
        """Processes the request with middlewares in forward order."""
        for middleware in self.middlewares:
            logger.debug("Processing request (%s) with middleware %s", request, middleware)
            new_request = middleware.process_request(request)
            if new_request is None:
                logger.warning("Middleware %s returned `None`, skipping remaining middlewares", middleware)
                return None

            request = new_request

        logger.debug("Request after processing: %s", request)
        return request

    def _render_message(self, request: MessageRequest) -> None:
        """Updates the request with rendered message, in-place."""
        if request.template_key is None:
            msg = "Template key is required to render the message"
            raise ValueError(msg)

        template = self._get_template(request.template_key)
        logger.debug("Rendering request %s with template: %s", request, template)
        rendered = template.render(request.context)
        request.body = MessageBody.model_validate(rendered)

    def _get_template(self, key: str) -> BaseTemplate:
        """Loads the template by key."""
        for loader in self.template_loaders:
            template = loader.load(key)
            if template is not None:
                return template

        msg = f"Template with key '{key}' not found"
        raise TemplateNotFoundError(msg)

    def _deliver_message(self, request: MessageRequest) -> MessageResponse:
        """Invoke the messaging backend to deliver the message."""
        logger.debug("Delivering message request: %s", request)
        response = self.messaging_backend.deliver(request)
        logger.debug("Response after delivery: %s", response)
        return response

    def _process_response(self, response: MessageResponse) -> MessageResponse | None:
        """Processes the response with middlewares in reverse order."""
        for middleware in reversed(self.middlewares):
            logger.debug("Processing response (%s) with middleware: %s", response, middleware)
            new_response = middleware.process_response(response)
            if new_response is None:
                logger.warning("Middleware %s returned `None`, skipping remaining middlewares", middleware)
                return None

            response = new_response

        logger.debug("Response after processing: %s", response)
        return response

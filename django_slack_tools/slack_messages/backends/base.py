"""Slack messaging backends."""

from __future__ import annotations

import dataclasses
import traceback
from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, cast

from slack_sdk.errors import SlackApiError

from django_slack_tools.slack_messages.models import SlackMessage, SlackMessagingPolicy
from django_slack_tools.slack_messages.response import MessageResponse
from django_slack_tools.utils.slack import MessageBody, MessageHeader
from django_slack_tools.utils.template import DictTemplate, DjangoTemplate

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse

    from django_slack_tools.slack_messages.models.mention import SlackMention
    from django_slack_tools.slack_messages.models.message_recipient import SlackMessageRecipient
    from django_slack_tools.slack_messages.request import MessageRequest
    from django_slack_tools.utils.template import BaseTemplate

logger = getLogger(__name__)

RESERVED_CONTEXT_KWARGS = frozenset({"policy", "mentions", "mentions_as_str"})
"""Set of reserved context keys automatically created."""


class BaseBackend(ABC):
    """Abstract base class for messaging backends."""

    def prepare_message(
        self,
        *,
        policy: SlackMessagingPolicy | None = None,
        channel: str,
        header: MessageHeader,
        body: MessageBody,
    ) -> SlackMessage:
        """Prepare message.

        Args:
            policy: Related policy instance.
            channel: Channel to send message.
            header: Slack message control header.
            body: Slack message body.

        Returns:
            Prepared message.
        """
        _header: dict = policy.header_defaults if policy else {}
        _header.update(dataclasses.asdict(header))

        _body = dataclasses.asdict(body)

        return SlackMessage(policy=policy, channel=channel, header=_header, body=_body)

    def prepare_messages_from_policy(
        self,
        policy: SlackMessagingPolicy,
        *,
        header: MessageHeader,
        context: dict[str, Any],
    ) -> list[SlackMessage]:
        """Prepare messages from policy.

        Args:
            policy: Policy to create messages from.
            header: Common message header.
            context: Message context.

        Returns:
            Prepared messages.
        """
        overridden_reserved = RESERVED_CONTEXT_KWARGS & set(context.keys())
        if overridden_reserved:
            logger.warning(
                "Template keyword argument(s) %s reserved for passing mentions, but already exists."
                " User provided value will override it.",
                ", ".join(f"`{s}`" for s in overridden_reserved),
            )

        messages: list[SlackMessage] = []
        for recipient in policy.recipients.all():
            logger.debug("Sending message to recipient %s", recipient)

            # Initialize template instance
            template = self._get_template_instance_from_policy(policy)

            # Prepare rendering arguments
            render_context = self._get_default_context(policy=policy, recipient=recipient)
            render_context.update(context)
            logger.debug("Context prepared as: %r", render_context)

            # Render template and parse as body
            rendered = template.render(context=render_context)
            body = MessageBody.from_any(rendered)

            # Create message instance
            message = self.prepare_message(policy=policy, channel=recipient.channel, header=header, body=body)
            messages.append(message)

        return SlackMessage.objects.bulk_create(messages)

    def _get_template_instance_from_policy(self, policy: SlackMessagingPolicy) -> BaseTemplate:
        """Get template instance."""
        if policy.template_type == SlackMessagingPolicy.TemplateType.DICT:
            return DictTemplate(policy.template)

        if policy.template_type == SlackMessagingPolicy.TemplateType.DJANGO:
            return DjangoTemplate(file=policy.template)

        if policy.template_type == SlackMessagingPolicy.TemplateType.DJANGO_INLINE:
            return DjangoTemplate(inline=policy.template)

        msg = f"Unsupported template type: {policy.template_type!r}"
        raise ValueError(msg)

    def _get_default_context(self, *, policy: SlackMessagingPolicy, recipient: SlackMessageRecipient) -> dict[str, Any]:
        """Get default context for rendering.

        Following default context keys are created:

        - `policy`: Policy code.
        - `mentions`: List of mentions.
        - `mentions_as_str`: Comma-separated joined string of mentions.
        """
        mentions: list[SlackMention] = list(recipient.mentions.all())
        mentions_as_str = ", ".join(mention.mention for mention in mentions)

        return {
            "policy": policy.code,
            "mentions": mentions,
            "mentions_as_str": mentions_as_str,
        }

    def send_messages(self, *messages: SlackMessage, raise_exception: bool, get_permalink: bool) -> int:
        """Shortcut to send multiple messages.

        Args:
            messages: Messages to send.
            raise_exception: Whether to propagate exceptions.
            get_permalink: Try to get the message permalink via additional Slack API call.

        Returns:
            Count of messages sent successfully.
        """
        num_sent = 0
        for message in messages:
            sent = self.send_message(message=message, raise_exception=raise_exception, get_permalink=get_permalink)
            num_sent += 1 if sent.ok else 0

        return num_sent

    def send_message(
        self,
        message: SlackMessage,
        *,
        raise_exception: bool,
        get_permalink: bool,
    ) -> SlackMessage:
        """Send message.

        Args:
            message: Prepared message.
            raise_exception: Whether to propagate exceptions.
            get_permalink: Try to get the message permalink via additional Slack API call.

        Returns:
            Message sent to Slack.
        """
        try:
            response: SlackResponse
            try:
                response = self._send_message(message)
            except SlackApiError as err:
                if raise_exception:
                    raise

                logger.warning(
                    "Error occurred while sending message but suppressed because `raise_exception` set.",
                    exc_info=err,
                )
                response = err.response

            message.ok = ok = cast(bool, response.get("ok"))
            if ok:
                # Get message TS if OK
                message.ts = cast(str, response.get("ts"))

                # Store thread TS if possible
                data: dict[str, Any] = response.get("message", {})
                message.parent_ts = data.get("thread_ts", "")

                # Get message permalink
                if get_permalink:
                    message.permalink = self._get_permalink(message=message, raise_exception=raise_exception)

            message.request = self._record_request(response)
            message.response = self._record_response(response)
        except:  # noqa: E722
            if raise_exception:
                raise

            logger.exception("Error occurred while sending message but suppressed because `raise_exception` set.")
            message.exception = traceback.format_exc()
        finally:
            message.save()

        message.refresh_from_db()
        return message

    # TODO(lasuillard): Temporary adaption for migration
    def deliver(self, request: MessageRequest) -> MessageResponse:
        """Deliver message request."""
        message = self.prepare_message(
            policy=None,
            channel=request.recipient,
            header=MessageHeader.from_any(request.headers),
            body=MessageBody.from_any(request.body),
        )
        message = self.send_message(message, raise_exception=True, get_permalink=False)
        return MessageResponse(
            request=request,
            is_sent=message.ok or False,
            error=message.exception,
            data=message.response,
        )

    @abstractmethod
    def _send_message(self, message: SlackMessage) -> SlackResponse:
        """Internal implementation of actual 'send message' behavior."""

    @abstractmethod
    def _get_permalink(self, *, message: SlackMessage, raise_exception: bool) -> str:
        """Get a permalink for given message identifier."""

    @abstractmethod
    def _record_request(self, response: SlackResponse) -> Any:
        """Extract request data to be recorded. Should return JSON-serializable object."""

    @abstractmethod
    def _record_response(self, response: SlackResponse) -> Any:
        """Extract response data to be recorded. Should return JSON-serializable object."""

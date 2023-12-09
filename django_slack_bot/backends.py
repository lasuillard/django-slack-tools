"""Slack messaging backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import Message

logger = getLogger(__name__)


class BackendBase(ABC):
    """Abstract base class for backends."""

    @abstractmethod
    def send_message(self, message: Message, *, raise_exception: bool = False) -> None:
        """Send given message."""


class DummyBackend(BackendBase):
    """An dummy backend that does nothing with message."""

    def send_message(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
        pass


class LoggingBackend(BackendBase):
    """Backend that log the message rather than sending it."""

    def send_message(self, message: Message, *args: Any, **kwargs: Any) -> None:  # noqa: D102, ARG002
        logger.debug("%r", message)


class SlackBackend(BackendBase):
    """Backend actually sending the messages."""

    def send_message(*args: Any, **kwargs: Any) -> None:  # noqa: D102
        # TODO(lasuillard): Send the message actually to channels
        raise NotImplementedError("TODO")  # noqa: EM101

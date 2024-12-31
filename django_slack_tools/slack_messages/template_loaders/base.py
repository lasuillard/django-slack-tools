# noqa: D100
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_slack_tools.slack_messages.message_templates import BaseTemplate


class BaseTemplateLoader(ABC):
    """Base class for template loaders."""

    @abstractmethod
    def load(self, key: str) -> BaseTemplate | None:
        """Load a template by key."""

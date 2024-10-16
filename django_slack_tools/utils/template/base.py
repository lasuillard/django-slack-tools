"""Abstraction for dictionary templates."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class BaseTemplate(ABC):
    """Abstract base class for dictionary templates."""

    @abstractmethod
    def render(self, *, context: dict[str, Any] | None = None) -> dict:
        """Render template with given context."""

# noqa: D100
# flake8: noqa: UP006, UP007, UP035
# ? Subscription syntax available since Python 3.10
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from django_slack_tools.slack_messages.request import MessageRequest  # noqa: TC001


class MessageResponse(BaseModel):
    """Response from a messaging backend."""

    request: Optional[MessageRequest] = None
    ok: bool
    error: Optional[Any] = None
    data: Any
    ts: Optional[str] = None
    parent_ts: Optional[str] = None

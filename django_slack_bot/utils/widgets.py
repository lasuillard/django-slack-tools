"""Django form widgets."""
from __future__ import annotations

import json
from logging import getLogger

from django.forms import widgets

logger = getLogger(__name__)


# Ref from: https://stackoverflow.com/a/52627264
class JSONWidget(widgets.Textarea):
    """Pretty formatted JSON widget."""

    indent = 2

    def format_value(self, value: str) -> str | None:  # noqa: D102
        try:
            value = json.dumps(json.loads(value), indent=self.indent)
            lines = value.split("\n")
            width, height = max(len(ln) for ln in lines), len(lines)
            self.attrs["rows"] = min(max(height + self.indent, 10), 40)  # 10 ~ 40
            self.attrs["cols"] = min(max(width + self.indent, 40), 120)  # 40 ~ 120
        except Exception:
            logger.exception("Error while formatting JSON object")

        return super().format_value(value)

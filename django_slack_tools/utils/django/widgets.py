"""Django form widgets."""

from __future__ import annotations

import json
from logging import getLogger

from django.forms import Textarea, TextInput

logger = getLogger(__name__)


# Ref from: https://stackoverflow.com/a/52627264
class JSONWidget(Textarea):
    """Pretty formatted JSON widget."""

    indent = 2

    def format_value(self, value: str) -> str | None:  # noqa: D102
        try:
            value = json.dumps(json.loads(value), indent=self.indent)
        except Exception:
            logger.exception("Error while formatting JSON object")

        # Calculate the size of the widget
        lines = value.split("\n")
        width, height = max(len(ln) for ln in lines), len(lines)
        self.attrs["rows"] = min(max(height + self.indent, 10), 40)  # 10 ~ 40
        self.attrs["cols"] = min(max(width + self.indent, 40), 120)  # 40 ~ 120

        return super().format_value(value)


class JSONTextInput(TextInput):
    """Widget for JSON field, but for string type specifically."""

    def format_value(self, value: str) -> str | None:  # noqa: D102
        value = value.encode().decode("unicode-escape").removeprefix('"').removesuffix('"')

        # Calculate the size of the widget
        self.attrs["size"] = min(max(len(value) + 5, 20), 80)  # 20 ~ 80

        return super().format_value(value)


class JSONTextarea(Textarea):
    """Widget for JSON field, but for string type specifically."""

    def format_value(self, value: str) -> str | None:  # noqa: D102
        value = value.encode().decode("unicode-escape").removeprefix('"').removesuffix('"')

        # Calculate the size of the widget
        lines = value.split("\n")
        width, height = max(len(ln) for ln in lines), len(lines)
        self.attrs["rows"] = min(max(height, 10), 40)  # 10 ~ 40
        self.attrs["cols"] = min(max(width, 40), 120)  # 40 ~ 120

        return super().format_value(value)

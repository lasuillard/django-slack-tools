# noqa: D100
import re

from django.db import models
from django.utils.translation import gettext_lazy as _


class MentionType(models.TextChoices):
    """Possible mention types."""

    USER = "U", _("User")
    "User mentions. e.g. `@lasuillard`."

    GROUP = "G", _("Group")
    "Team mentions. e.g. `@backend`."

    SPECIAL = "S", _("Special")
    "Special mentions. e.g. `@here`, `@channel`, `@everyone`."

    UNKNOWN = "?", _("Unknown")
    "Unknown mention type."

    @classmethod
    def infer(cls, mention: str) -> "MentionType":
        """Guess given mention's type."""
        if is_user_mention(mention):
            return cls.USER

        if is_group_mention(mention):
            return cls.GROUP

        if is_special_mention(mention):
            return cls.SPECIAL

        return cls.UNKNOWN


def is_user_mention(mention: str) -> bool:
    """Determine given mention string is user mention."""
    return bool(re.match(r"<@[0-9A-Z]+>", mention))


def is_group_mention(mention: str) -> bool:
    """Determine given mention string is group mention."""
    return bool(re.match(r"<!subteam^[0-9A-Z]+>", mention))


def is_special_mention(mention: str) -> bool:
    """Determine given mention string is special mention."""
    return mention in ("<!here>", "<!all>", "<!everyone>")

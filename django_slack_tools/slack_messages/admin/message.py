# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django_slack_tools.slack_messages.models import SlackMessage
from django_slack_tools.utils.django.widgets import JSONWidget

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise


@admin.register(SlackMessage)
class SlackMessageAdmin(admin.ModelAdmin):
    """Admin for messages."""

    readonly_fields = ("id", "_link_to_permalink", "created", "last_modified")

    @admin.display(description=_("Permalink"))
    def _link_to_permalink(self, instance: SlackMessage) -> StrOrPromise:
        url = instance.permalink
        if not url:
            return _("N/A")

        return format_html("<a href='{url}'>{title}</a>", url=url, title=_("Permalink"))

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "created"
    search_fields = ("id", "ts", "parent_ts", "policy__code", "channel")
    list_display = (
        "id",
        "ts",
        "ok",
        "policy",
        "channel",
        "parent_ts",
        "_link_to_permalink",
        "created",
        "last_modified",
    )
    list_display_links = ("id", "ts")
    list_select_related = ("policy",)
    list_filter = (
        "policy",
        "ok",
        ("created", DateFieldListFilter),
        ("last_modified", DateFieldListFilter),
    )

    # Change
    # ------------------------------------------------------------------------
    formfield_overrides = {  # noqa: RUF012
        models.JSONField: {"widget": JSONWidget},
    }
    fieldsets = (
        (
            None,
            {
                "fields": ("policy", "channel", "ok", "ts", "parent_ts", "_link_to_permalink", "header", "body"),
            },
        ),
        (
            _("Miscellaneous"),
            {
                "fields": ("id", "request", "response", "created", "last_modified"),
                "classes": ("collapse",),
            },
        ),
    )
    autocomplete_fields = ("policy",)

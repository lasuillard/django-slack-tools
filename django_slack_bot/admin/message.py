# noqa: D100
from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.utils.translation import gettext_lazy as _

from django_slack_bot.models import SlackMessage


@admin.register(SlackMessage)
class SlackMessageAdmin(admin.ModelAdmin):
    """Admin for messages."""

    readonly_fields = ("id", "created", "last_modified")

    # Actions
    actions = ()
    actions_on_bottom = True  # Likely to be there are lots of messages

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "created"
    search_fields = ("id", "ts", "parent_ts", "policy__code", "channel")
    list_display = ("id", "ts", "ok", "policy", "channel", "parent_ts", "created", "last_modified")
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
    fieldsets = (
        (
            None,
            {
                "fields": ("policy", "channel", "ok", "ts", "parent_ts", "body"),
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

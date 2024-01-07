# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from django_slack_bot.models import SlackMessageRecipient
from django_slack_bot.utils.slack import get_workspace_info

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django_stubs_ext import StrOrPromise

    class SlackMessageRecipientWithAnnotates(SlackMessageRecipient):  # noqa: D101
        num_mentions: int


@admin.register(SlackMessageRecipient)
class SlackMessageRecipientAdmin(admin.ModelAdmin):
    """Admin for recipients."""

    def get_queryset(self, request: HttpRequest) -> QuerySet[SlackMessageRecipientWithAnnotates]:  # noqa: D102
        return cast(
            QuerySet["SlackMessageRecipientWithAnnotates"],  # Unsafe force type casting
            super()
            .get_queryset(request)
            .annotate(
                # Avoid calling `.recipients.count()` per records
                num_mentions=Count("mentions"),
            ),
        )

    @admin.display(description=_("Channel Name"))
    def _get_channel_name(self, instance: SlackMessageRecipient) -> StrOrPromise:
        workspace_info = get_workspace_info()
        if workspace_info is None:
            return _("N/A")

        for channel in workspace_info.channels:
            if channel["id"] == instance.channel:
                return "#{channel}".format(channel=channel["name"])

        # In cases of channel not exist, bot is not in channel, DM between user and bot, etc.
        return _("?")

    readonly_fields = ("id", "_get_channel_name", "created", "last_modified")

    # Actions
    actions = ()

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("alias", "channel", "mentions__mention")
    list_display = ("id", "alias", "channel", "_get_channel_name", "_num_mentions", "created", "last_modified")
    list_display_links = ("id", "alias")
    list_filter = (
        ("created", DateFieldListFilter),
        ("last_modified", DateFieldListFilter),
    )

    @admin.display(description=_("Number of Mentions"))
    def _num_mentions(self, instance: SlackMessageRecipientWithAnnotates) -> int:
        return instance.num_mentions

    # Change
    # ------------------------------------------------------------------------
    fieldsets = (
        (
            None,
            {
                "fields": ("alias", "channel", "_get_channel_name", "mentions"),
            },
        ),
        (
            _("Miscellaneous"),
            {
                "fields": ("id", "created", "last_modified"),
                "classes": ("collapse",),
            },
        ),
    )

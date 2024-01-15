# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import admin, messages
from django.contrib.admin.filters import DateFieldListFilter
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from django_slack_bot.app_settings import app_settings
from django_slack_bot.models import SlackMessageRecipient

if TYPE_CHECKING:
    from django.http import HttpRequest

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

    readonly_fields = ("id", "created", "last_modified")

    # Actions
    actions = ("_update_channel_names",)

    @admin.action(description=_("Update recipient' channel names"))
    def _update_channel_names(self, request: HttpRequest, queryset: QuerySet[SlackMessageRecipient]) -> None:
        """Admin action to update selected recipients' channel names using workspace info."""
        channels = _get_channels()

        # Temporary changes
        changes: list[SlackMessageRecipient] = []
        failures: list[SlackMessageRecipient] = []
        for recipient in queryset:
            match = channels.get(recipient.channel)
            if match is None:
                failures.append(recipient)
                continue

            recipient.channel_name = f"#{match}"
            changes.append(recipient)

        # Bulk update in single query
        n_success = SlackMessageRecipient.objects.bulk_update(changes, fields=("channel_name",))

        # Reporting
        if failures:
            messages.warning(
                request,
                _(
                    "Updated {n_success} recipients successfully"
                    " and there were {n_fail} recipients failed to update because no matching data.",
                ).format(n_success=n_success, n_fail=len(failures)),
            )
        else:
            messages.info(request, _("Updated {n} recipients.").format(n=n_success))

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("alias", "channel_name", "channel", "mentions__mention")
    list_display = ("id", "alias", "channel_name", "_num_mentions", "created", "last_modified")
    list_display_links = ("id", "alias", "channel_name")
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
                "fields": ("alias", "channel", "channel_name", "mentions"),
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


def _get_channels() -> dict[str, str]:
    # TODO(lasuillard): Need pagination in future
    response = app_settings.slack_app.client.conversations_list()
    channels: list[dict] = response.get("channels", default=[])
    return {channel["id"]: channel["name"] for channel in channels}

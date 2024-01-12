# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from django.contrib import admin, messages
from django.contrib.admin.filters import ChoicesFieldListFilter, DateFieldListFilter
from django.utils.translation import gettext_lazy as _

from django_slack_bot.app_settings import app_settings
from django_slack_bot.models import SlackMention

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest


@admin.register(SlackMention)
class SlackMentionAdmin(admin.ModelAdmin):
    """Admin for recipients."""

    readonly_fields = ("id", "_get_mention_str", "created", "last_modified")

    @admin.display(description=_("Mention string"))
    def _get_mention_str(self, instance: SlackMention) -> str:
        return instance.mention

    # Actions
    actions = ("_update_mentions",)

    @admin.action(description=_("Update type and name of mentions"))
    def _update_mentions(self, request: HttpRequest, queryset: QuerySet[SlackMention]) -> None:
        """Admin action to update selected mentions' type and name using Slack workspace information."""
        items = _get_mentionable_items()

        # Iterate over all make temporary updates
        changes: list[SlackMention] = []
        failures: list[SlackMention] = []
        for mention in queryset:
            match = items.get(mention.mention_id)
            if match is None:
                failures.append(mention)
                continue

            mention.type = match["type"]
            mention.name = match["name"]
            changes.append(mention)

        # Make changes in bulk
        n_success = SlackMention.objects.bulk_update(changes, fields=("type", "name"))

        # Report back to admin
        if failures:
            messages.warning(
                request,
                _(
                    "Updated {n_success} mentions successfully"
                    " and there were {n_fail} mentions failed to update because no matching data.",
                ).format(n_success=n_success, n_fail=len(failures)),
            )
        else:
            messages.info(request, _("Updated {n} mentions.").format(n=n_success))

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("name", "mention_id")
    list_display = ("id", "name", "type", "mention_id", "created", "last_modified")
    list_display_links = ("id", "name", "mention_id")
    list_filter = (
        ("type", ChoicesFieldListFilter),
        ("created", DateFieldListFilter),
        ("last_modified", DateFieldListFilter),
    )

    # Change
    # ------------------------------------------------------------------------
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "type", "mention_id", "_get_mention_str"),
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


def _get_mentionable_items() -> dict[str, _Mentionable]:
    """Returns mapping of ID to mention name for members and usergroups."""
    # Fetch members from Slack
    # TODO(lasuillard): Need pagination in future
    response = app_settings.slack_app.client.users_list()
    if not response.get("ok", False):
        return {}

    members: list[dict] = response.get("members", default=[])

    # Fetch usergroups from Slack
    response = app_settings.slack_app.client.usergroups_list()
    if not response.get("ok", False):
        return {}

    usergroups: list[dict] = response.get("usergroups", default=[])

    # List of mentionable
    items: dict[str, _Mentionable] = {}

    # Members mapping
    items.update(
        {
            member["id"]: {
                "type": SlackMention.MentionType.USER,
                "name": member["profile"]["display_name"] or member["profile"]["real_name"],
            }
            for member in members
        },
    )

    # Usergroups mapping
    items.update(
        {
            usergroup["id"]: {
                "type": SlackMention.MentionType.GROUP,
                "name": usergroup["name"],
            }
            for usergroup in usergroups
        },
    )

    return items


class _Mentionable(TypedDict):
    type: SlackMention.MentionType
    name: str

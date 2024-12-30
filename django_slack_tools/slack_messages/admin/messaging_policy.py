# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django_slack_tools.slack_messages.models import SlackMessagingPolicy
from django_slack_tools.utils.django.widgets import JSONWidget
from django_slack_tools.utils.slack import get_block_kit_builder_url

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django_stubs_ext import StrOrPromise

    # I can't make any better idea for my experience, extending model instance with annotates
    # If you, reader, knows better one, plz make PR :)
    # NOTE: Pylance complains `django_stubs_ext.WithAnnotations` about its call signature
    class SlackMessagingPolicyWithAnnotates(SlackMessagingPolicy):  # noqa: D101
        num_recipients: int

else:
    SlackMessagingPolicyWithAnnotates = SlackMessagingPolicy


@admin.register(SlackMessagingPolicy)
class SlackMessagingPolicyAdmin(admin.ModelAdmin):
    """Admin for messaging policies."""

    def get_queryset(self, request: HttpRequest) -> QuerySet[SlackMessagingPolicyWithAnnotates]:  # noqa: D102
        return cast(
            QuerySet["SlackMessagingPolicyWithAnnotates"],  # Unsafe force type casting
            super()
            .get_queryset(request)
            .annotate(
                # Avoid calling `.recipients.count()` per records
                num_recipients=Count("recipients"),
            ),
        )

    readonly_fields = (
        "id",
        "_count_recipients",
        "_blocks_block_kit_builder_url",
        "_attachments_block_kit_builder_url",
        "created",
        "last_modified",
    )

    @admin.display(description=_("Number of Recipients"))
    def _count_recipients(self, instance: SlackMessagingPolicyWithAnnotates) -> int:
        return instance.num_recipients

    @admin.display(description=_("Blocks Preview"))
    def _blocks_block_kit_builder_url(self, instance: SlackMessagingPolicy) -> StrOrPromise:
        """Generate shortcut URL to Slack Block Kit Builder page for current policy template."""
        template = instance.template
        if not instance.template:
            return _("Template is empty, no link available.")

        if "blocks" not in template:
            return _("Template has no blocks.")

        url = get_block_kit_builder_url(blocks=template["blocks"])
        return format_html("<a href='{url}'>Link to Block Kit Builder</a>", url=url)

    @admin.display(description=_("Attachments Preview"))
    def _attachments_block_kit_builder_url(self, instance: SlackMessagingPolicy) -> StrOrPromise:
        """Generate shortcut URL to Slack Block Kit Builder page for current policy template."""
        template = instance.template
        if not instance.template:
            return _("Template is empty, no link available.")

        if "attachments" not in template:
            return _("Template has no attachments.")

        url = get_block_kit_builder_url(attachments=template["attachments"])
        return format_html("<a href='{url}'>Link to Block Kit Builder</a>", url=url)

    # Actions
    actions = ()

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("code",)
    list_display = ("id", "code", "enabled", "_count_recipients", "created", "last_modified")
    list_display_links = ("id", "code")
    list_filter = (
        "enabled",
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
                "fields": ("code", "enabled", "recipients", "header_defaults", "template"),
            },
        ),
        (
            _("Utility"),
            {
                "fields": ("_blocks_block_kit_builder_url", "_attachments_block_kit_builder_url"),
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
    autocomplete_fields = ("recipients",)

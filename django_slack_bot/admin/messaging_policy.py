# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from django_slack_bot.models import SlackMessagingPolicy

if TYPE_CHECKING:
    from django.http import HttpRequest

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

    readonly_fields = ("id", "_count_recipients", "created", "last_modified")

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

    @admin.display(description=_("Number of Recipients"))
    def _count_recipients(self, instance: SlackMessagingPolicyWithAnnotates) -> int:
        return instance.num_recipients

    # Change
    # ------------------------------------------------------------------------
    fieldsets = (
        (
            None,
            {
                "fields": ("code", "enabled", "recipients", "template"),
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

# noqa: D100
from django.contrib import admin
from django.contrib.admin.filters import ChoicesFieldListFilter, DateFieldListFilter
from django.utils.translation import gettext_lazy as _

from django_slack_bot.models import SlackMention


@admin.register(SlackMention)
class SlackMentionAdmin(admin.ModelAdmin):
    """Admin for recipients."""

    readonly_fields = ("id", "created", "last_modified")

    # Actions
    actions = ()

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("name", "mention")
    list_display = ("id", "name", "type", "mention", "created", "last_modified")
    list_display_links = ("id", "name", "mention")
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
                "fields": ("name", "type", "mention"),
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

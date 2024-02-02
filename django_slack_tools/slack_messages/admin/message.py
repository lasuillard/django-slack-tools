# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING

import django.contrib.messages
from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django_slack_tools.app_settings import app_settings
from django_slack_tools.slack_messages.models import SlackMessage
from django_slack_tools.utils.widgets import JSONWidget

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest
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

    # Actions
    actions = ("_clone_messages", "_send_messages")
    actions_on_bottom = True  # Likely to be there are lots of messages

    @admin.action(description=_("Clone messages"))
    def _clone_messages(self, request: HttpRequest, queryset: QuerySet[SlackMessage]) -> None:
        messages = list(queryset)
        for message in queryset:
            message.pk = None
            message.ts = None
            message.parent_ts = ""
            message.ok = None
            message.request = None
            message.response = None

        created = SlackMessage.objects.bulk_create(messages)
        n = len(created)
        django.contrib.messages.info(request, _("Cloned {n} messages.").format(n=n))

    @admin.action(description=_("Send messages"))
    def _send_messages(self, request: HttpRequest, queryset: QuerySet[SlackMessage]) -> None:
        backend = app_settings.backend

        # Send selected messages
        n_success = 0
        n_failure = 0
        for message in queryset:
            backend.send_message(message, raise_exception=False)
            if message.ok:
                n_success += 1
            else:
                n_failure += 1

        # Notify result to user
        n = n_success + n_failure
        if n_failure:
            django.contrib.messages.info(
                request,
                _("Tried to send {n} messages, {n_success} succeeded and {n_failure} failed.").format(
                    n=n,
                    n_success=n_success,
                    n_failure=n_failure,
                ),
            )
        else:
            django.contrib.messages.info(request, _("Sent {n} messages.").format(n=n))

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

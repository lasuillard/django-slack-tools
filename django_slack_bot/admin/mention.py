# noqa: D100
from django.contrib import admin
from django.contrib.admin.filters import ChoicesFieldListFilter, DateFieldListFilter
from django.utils.translation import gettext_lazy as _

from django_slack_bot.app_settings import app_settings
from django_slack_bot.choices import MentionType
from django_slack_bot.models import SlackMention


@admin.register(SlackMention)
class SlackMentionAdmin(admin.ModelAdmin):
    """Admin for recipients."""

    readonly_fields = ("id", "_get_mention_name", "created", "last_modified")

    @admin.display(description=_("Mention Name"))
    def _get_mention_name(self, instance: SlackMention) -> str:
        workspace_info = app_settings.backend.get_workspace_info()

        if instance.type == MentionType.USER:
            for member in workspace_info.members:
                if "<@{id}>".format(id=member["id"]) == instance.mention:
                    return str(member["profile"]["display_name"])
            return "?"

        if instance.type == MentionType.GROUP:
            for usergroup in workspace_info.usergroups:
                if "<!subteam^{id}>".format(id=usergroup["id"]) == instance.mention:
                    return str(usergroup["name"])
            return "?"

        return ""

    # Actions
    actions = ()

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("name", "mention")
    list_display = ("id", "name", "type", "mention", "_get_mention_name", "created", "last_modified")
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
                "fields": ("name", "type", "mention", "_get_mention_name"),
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

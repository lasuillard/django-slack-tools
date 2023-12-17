# noqa: D100
from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.utils.translation import gettext_lazy as _

from django_slack_bot.models import SlackMessageRecipient

# TODO(lasuillard): Choice field for recipients (via Slack API)
# TODO(lasuillard): Override admin to display Slack workspace information (what Bot detect)
#                   > channels, users, ... (and there ID)


@admin.register(SlackMessageRecipient)
class SlackMessageRecipientAdmin(admin.ModelAdmin):
    """Admin for recipients."""

    readonly_fields = ("id", "created", "last_modified")

    # Actions
    actions = ()

    # Changelist
    # ------------------------------------------------------------------------
    date_hierarchy = "last_modified"
    search_fields = ("alias", "channel")  # TODO(lasuillard): Search by mention
    list_display = ("id", "alias", "channel", "_num_mentions", "created", "last_modified")
    list_display_links = ("id", "alias")
    list_filter = (
        ("created", DateFieldListFilter),
        ("last_modified", DateFieldListFilter),
    )

    @admin.display(description=_("Number of Mentions"))
    def _num_mentions(self, instance: SlackMessageRecipient) -> int:
        return len(instance.mentions)

    # Change
    # ------------------------------------------------------------------------
    fieldsets = (
        (
            None,
            {
                "fields": ("alias", "channel", "mentions"),
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

    # TODO(lasuillard): Related policy model inline

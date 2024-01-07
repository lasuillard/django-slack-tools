"""Module for Slack workspace."""
from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, List

from django.core.cache import cache
from pydantic import BaseModel, ValidationError

from django_slack_bot.utils.cache import generate_cache_key

if TYPE_CHECKING:
    from slack_bolt import App


logger = getLogger(__name__)


def get_workspace_info(app: App | None = None) -> WorkspaceInfo | None:
    """Retrieve Slack workspace info.

    Args:
        app: Slack app.

    Returns:
        Slack workspace info.
    """
    from django_slack_bot.app_settings import app_settings

    app = app or app_settings.slack_app
    if app is None:
        return WorkspaceInfo(team={}, members=[], usergroups=[], channels=[])

    cache_key = generate_cache_key(get_workspace_info.__name__)
    if cached := cache.get(cache_key):
        try:
            return WorkspaceInfo.model_validate(cached)
        except ValidationError:
            cache.delete(cache_key)
            logger.exception("Failed to validate cached workspace info. Cache has been invalidated.")

    team: dict = app.client.team_info().get("team", default={})

    # TODO(lasuillard): For large workspace (users > 200?) it should handle pagination in future
    #                   but not considering it for now
    members: list[dict] = app.client.users_list().get("members", default=[])
    usergroups: list[dict] = app.client.usergroups_list().get("usergroups", default=[])
    channels: list[dict] = app.client.conversations_list().get("channels", default=[])

    info = WorkspaceInfo(
        team=team,
        members=members,
        usergroups=usergroups,
        channels=channels,
    )
    cache.set(key=cache_key, value=info.model_dump(), timeout=60 * 60)
    return info


class WorkspaceInfo(BaseModel):
    """Slack workspace info."""

    # https://api.slack.com/methods/team.info
    team: dict

    # https://api.slack.com/methods/users.list
    members: List[dict]  # noqa: UP006

    # https://api.slack.com/methods/usergroups.list
    usergroups: List[dict]  # noqa: UP006

    # https://api.slack.com/methods/conversations.list
    channels: List[dict]  # noqa: UP006

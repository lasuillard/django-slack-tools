import pytest

from django_slack_tools.utils.slack import get_block_kit_builder_url


def test_get_block_kit_builder_url() -> None:
    with pytest.raises(ValueError, match="Only one of `blocks` or `attachments` should be provided."):
        get_block_kit_builder_url()

    with pytest.raises(ValueError, match="Only one of `blocks` or `attachments` should be provided."):
        get_block_kit_builder_url(blocks=[], attachments=[])

    payload = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Hello, World!",
            },
        },
    ]

    # Without team ID; just hoping the browser to take user right place (Slack may redirect with team ID if logged in)
    url = get_block_kit_builder_url(blocks=payload)
    assert (
        url
        == "https://app.slack.com/block-kit-builder/#%7B%22blocks%22%3A%20%5B%7B%22type%22%3A%20%22section%22%2C%20%22text%22%3A%20%7B%22type%22%3A%20%22mrkdwn%22%2C%20%22text%22%3A%20%22Hello%2C%20World%21%22%7D%7D%5D%7D"
    )

    url = get_block_kit_builder_url(attachments=payload)
    assert (
        url
        == "https://app.slack.com/block-kit-builder/#%7B%22attachments%22%3A%20%5B%7B%22type%22%3A%20%22section%22%2C%20%22text%22%3A%20%7B%22type%22%3A%20%22mrkdwn%22%2C%20%22text%22%3A%20%22Hello%2C%20World%21%22%7D%7D%5D%7D"
    )

    # With team ID
    url = get_block_kit_builder_url(team_id="T00000000", blocks=payload)
    assert (
        url
        == "https://app.slack.com/block-kit-builder/T00000000#%7B%22blocks%22%3A%20%5B%7B%22type%22%3A%20%22section%22%2C%20%22text%22%3A%20%7B%22type%22%3A%20%22mrkdwn%22%2C%20%22text%22%3A%20%22Hello%2C%20World%21%22%7D%7D%5D%7D"
    )

    url = get_block_kit_builder_url(team_id="T00000000", attachments=payload)
    assert (
        url
        == "https://app.slack.com/block-kit-builder/T00000000#%7B%22attachments%22%3A%20%5B%7B%22type%22%3A%20%22section%22%2C%20%22text%22%3A%20%7B%22type%22%3A%20%22mrkdwn%22%2C%20%22text%22%3A%20%22Hello%2C%20World%21%22%7D%7D%5D%7D"
    )

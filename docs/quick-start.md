
## 🚀 Installation

**django-slack-tools** supports Python 3.9+ and Django 4.2+. Supports for each deps will be dropped as soon as the ends of security updates.

> [!WARNING]
> 0.x versions are for development. Breaking changes can be made at any time. If gonna use this package, recommend to pin down the version.

Install the package:

```bash
$ pip install django-slack-tools
```

Add the app to the your Django settings:

```python
INSTALLED_APPS = [
    ...
    "django.contrib.messages", # Used in admin
    "django_slack_tools.slack_messages",
    ...
]
```

Add configuration for application:

```python
DJANGO_SLACK_TOOLS = {
    "messengers": {
        "default": {
            "class": "django_slack_tools.slack_messages.messenger.Messenger",
            "kwargs": {
                "template_loaders": [
                    "django_slack_tools.slack_messages.template_loaders.DjangoTemplateLoader",
                ],
                "middlewares": [],
                "messaging_backend": {
                    "class": "django_slack_tools.slack_messages.backends.SlackBackend",
                    "kwargs": {
                        "slack_app": "<module.path.to.your-slack-app>",
                    },
                },
            },
        },
    }
}
```

Then, run the database migration and create `greet.xml` file in `templates/` directory:

```xml
<root>
    <block type="section">
        <text type="mrkdwn">
            {{ greet }}
        </text>
    </block>
</root>
```

Send a message:

```python
from django_slack_tools.slack_messages.shortcuts import slack_message

message = slack_message(
    "<channel-id>",
    template="greet.xml",
    context={"greet": "Hello, World!"},
)
```

Please check the examples for more about details.

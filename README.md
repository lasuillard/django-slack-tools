# django-slack-tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/lasuillard/django-slack-tools/actions/workflows/ci.yaml/badge.svg)](https://github.com/lasuillard/django-slack-tools/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/lasuillard/django-slack-tools/graph/badge.svg?token=c8kzjqjplF)](https://codecov.io/gh/lasuillard/django-slack-tools)
![PyPI - Version](https://img.shields.io/pypi/v/django-slack-tools)

Little helpers working with Slack bot 🤖 in Django.

This project aims to implementing helpful features making Slack bot and providing reusable Django apps integrated with database.

## ✨ Features

Key features are:

- [x] Reusable Django app for Slack messaging with various messaging backends for different environments

- [x] Database-backed Slack messaging policies with simple dictionary-based template

- [x] Message histories

- [x] Built-in admin for management working with Slack workspace

- [x] Celery support for messaging backends, management and shortcut tasks, etc.

- [x] Django template support

And more in future roadmap...

- [ ] New Django apps and helpers for Slack features such as modals, event subscription, etc.

- [ ] More fine working example with rich documentation

Currently it is focused on messaging features. In future, hoping to bring more helpful features across Slack Bot ecosystem, such as event subscriptions, modals, bot interactions, etc.

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

Please check the [documentation](https://lasuillard.github.io/django-slack-tools/) and [examples](./examples/) for more about details.

## 💖 Contributing

All contributions and helps are welcome. Please check the [CONTRIBUTING.md](./CONTRIBUTING.md) file for about details.

## 📜 License

This project is licensed under the terms of the MIT license.

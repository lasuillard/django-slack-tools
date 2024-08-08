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

And more in future roadmap...

- [ ] Celery support for messaging backends, management and shortcut tasks, etc.
- [ ] Django template support
- [ ] New Django apps and helpers for Slack features such as modals, event subscription, etc.

Currently it is focused on messaging features. In future, hoping to bring more helpful features across Slack Bot ecosystem, such as event subscriptions, modals, bot interactions, etc.

## 🚀 Installation

**django-slack-tools** supports Python 3.8+ and Django 4.2+. Supports for each deps will be dropped as soon as the ends of security updates.

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
    # Module path to Slack Bolt application or callable returns the app
    "SLACK_APP": "path.to.your.slack.app",

    # Messaging backend configuration
    "BACKEND": {
        "NAME": "django_slack_tools.slack_messages.backends.SlackBackend",
        "OPTIONS": {
            # TODO(#44): Reasonable defaults to reduce some duplicates
            "slack_app": "path.to.your.slack.app",
        }
    }
}
```

Then, run the database migration and send messages:

```python
from django_slack_tools.slack_messages.message import slack_message

message = slack_message(
    "I like threading",
    channel="id-of-channel",
    header={"reply_broadcast": True},
)
```

Please check the [documentation](https://lasuillard.github.io/django-slack-tools/) for more about details.

## 💖 Contributing

All contributions and helps are welcome. Please check the [CONTRIBUTING.md](./CONTRIBUTING.md) file for about details.

## 📜 License

This project is licensed under the terms of the MIT license.

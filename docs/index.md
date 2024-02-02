# django-slack-bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/lasuillard/django-slack-bot/actions/workflows/ci.yaml/badge.svg)](https://github.com/lasuillard/django-slack-bot/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/lasuillard/django-slack-bot/graph/badge.svg?token=c8kzjqjplF)](https://codecov.io/gh/lasuillard/django-slack-bot)

Little helpers working with Slack bot 🤖 in Django.

This project aims to implementing helpful features making Slack bot and providing reusable Django apps integrated with database.

## Features

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

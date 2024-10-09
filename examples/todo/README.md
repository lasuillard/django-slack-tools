# Example To Do app

Simple To Do bot example with Django Slack Tools.

## Features

- Show recent To Do from app home

- Create or mark it done a To Do from Slack shortcuts via modals

- Notify to Slack channel if To Do created or updated using Django signals

## Create Slack app

This example uses event subscription and messaging features. As Slack documentation suggest, We'd recommend to use ngrok for it. See [link](https://api.slack.com/start/building/bolt-python).

Required scopes to bot fully work (including admin pages):

- **app_mentions:read**
- **channels:read**
- **chat:write**
- **chat:write.customize**
- **commands**
- **team:read**
- **usergroups:read**
- **users:read**

## Run application

```bash
# Initialize
$ uv run python manage.py migrate

# Create superuser
$ uv run python manage.py createsuperuser

# Run server with environment variables set
$ export SLACK_BOT_TOKEN='...'
$ export SLACK_SIGNING_SECRET='...'
$ uv run python manage.py runserver 0.0.0.0:8000
```

Once server started, open a new terminal and run ngrok for event subscription.

```bash
# Run ngrok server to get Slack events
$ ngrok http 8000
```

Go to the Slack bot settings and configure event subscription with given ngrok URL.

Once all setup is done, you will see shortcuts in Slack chat if you type slash(/).

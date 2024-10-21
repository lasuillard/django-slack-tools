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

Create .env file with content:

```dotenv
SLACK_BOT_TOKEN='...'
SLACK_SIGNING_SECRET='...'
```

```bash
# Run Postgres and Valkey services
$ docker compose up -d

# Initialize database
$ make migrate

# Create superuser
$ make superuser

# Run Django web server, then open http://localhost:8000/admin to open admin page
$ source .env && make run

# (Recommended) To test full functionality, create new terminal and run Celery worker
$ source .env && make run-celery-worker

# (Optional) To test periodic tasks, create another new terminal and run Celery Beat scheduler
$ source .env && make run-celery-beat
```

Once server started, open a new terminal and run ngrok for event subscription.

```bash
# Add auth token for ngrok if not set yet
$ ngrok config add-authtoken '...'

# Run ngrok server (with free static domain for later re-run) to get Slack events
$ ngrok http 8000 --domain '....ngrok.free.app'
```

Go to the Slack bot settings and configure event subscription with given ngrok URL. If you are seeing 401 errors in ngrok traffic logs, check your bot credentials.

Once all setup is done, you will see shortcuts in Slack chat if you type slash(/).

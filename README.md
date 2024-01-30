# RoverChatBot

## Prerequisites

1. Install Docker
2. Make an account on OpenAI to get an API key
3. Get added to Supabase Team Org. You will need URL and Key

## How to create Python instance on MacOS

```
python3 -m venv venv
source venv/bin/activate
pip install openai twilio 'flask[async]' python-dotenv pyngrok black termcolor supabase flask-cors ringcentral 'sentry-sdk[flask]'
```

## How to create Python instance on Windows

```
python -m venv venv
venv/scripts/Activate.ps1   # if using Powershell in terminal
pip install openai twilio 'flask[async]' python-dotenv pyngrok black termcolor supabase flask-cors flask ringcentral
```

## How to start server

```
flask run --port 8000 --debug
```

## How to use Ngrok for testing

(you will probably need to go make your own account https://ngrok.com/ and set it up)

```
ngrok http --domain=doe-up-muskox.ngrok-free.app 8000
```

## Local Development

Log in if you are planning to deploy your project to the Supabase Platform. This step is optional and is not required to use the Supabase CLI.

```
supabase login
```

Initialize Supabase to set up the configuration for developing your project locally:

```
supabase init
```

Make sure Docker is running

The start command uses Docker to start the Supabase services.
This command may take a while to run if this is the first time using the CLI.

```
supabase start
```

You can use the supabase stop command at any time to stop all services (without resetting your local database). Use supabase stop --no-backup to stop all services and reset your local database.

To create a migration, then push it to remote

```
supabase db diff -f nameOfNewMigration
supabase db push
```

to pull changes from remote database, then apply them

```
supabase db pull
supabase db reset
```

### Access your project's services

You can now visit your local Dashboard at http://localhost:54323, and access the database directly with any Postgres client via postgresql://postgres:postgres@localhost:54322/postgres.

```
# Default URL:
postgresql://postgres:postgres@localhost:54322/postgres
```

The local Postgres instance can be accessed through psql
or any other Postgres client, such as pgadmin.

For example:

```
psql 'postgresql://postgres:postgres@localhost:54322/postgres'
```

## Formatting

```
black .
```

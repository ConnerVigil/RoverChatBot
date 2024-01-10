# RoverChatBot

## How to create Python instance

```
python3 -m venv venv
source venv/bin/activate
pip install openai twilio 'flask[async]' python-dotenv pyngrok black
```

## How to start server

```
flask run --port 8000 --debug
```

## How to use Ngrok for testing

```
ngrok http --domain=doe-up-muskox.ngrok-free.app 8000
```

## Linux Services

```
#Reload the service files to include the new service.
sudo systemctl daemon-reload


#Start your service
sudo systemctl start your-service.service

#To check the status of your service
sudo systemctl status example.service

#To enable your service on every reboot
sudo systemctl enable example.service

#To disable your service on every reboot
sudo systemctl disable example.service
```

## NGINX

```
sudo systemctl restart nginx
```

## GUNICORN

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

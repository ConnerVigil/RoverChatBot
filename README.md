# RoverChatBot

## How to create Python instance

```
python3 -m venv venv
source venv/bin/activate
pip install openai twilio flask[async] python-dotenv pyngrok
```

## How to start server

```
flask run --port 8000 --debug
```

## How to use Ngrok for testing

```
ngrok http 8000
```

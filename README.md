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
ngrok http 8000
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

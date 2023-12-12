from flask import Flask, request, session, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import askgpt, send_message
import os
from dotenv import load_dotenv

load_dotenv()

# Since session cookies are signed, the Flask application
# needs to have a secret key configured to be able to
# generate signatures.
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/bot", methods=["POST"])
async def bot():
    incoming_msg = request.values["Body"]
    sender_number = request.values["From"]
    twilio_number = request.values["To"]
    await async_helper(incoming_msg, sender_number, twilio_number)
    return Response(status=204)


async def async_helper(question, sender_number, twilio_number):
    chat_log = session.get("chat_log")
    answer, chat_log = askgpt(question, chat_log)
    session["chat_log"] = chat_log
    await send_message(answer, sender_number, twilio_number)
    return


@app.route("/backup", methods=["GET"])
def backup():
    response = MessagingResponse()
    response.message("Sorry, our AI took too long to respond 😢")
    return str(response)


@app.route("/greeting", methods=["GET"])
async def greeting():
    sender_number = request.values["From"]
    twilio_number = request.values["To"]
    await send_message(
        "Hello, sorry we missed your call. How can I help you?",
        sender_number,
        twilio_number,
    )
    response = VoiceResponse()
    response.hangup()
    return str(response)


# python3 -m venv venv
# source venv/bin/activate
# pip install openai twilio flask python-dotenv pyngrok

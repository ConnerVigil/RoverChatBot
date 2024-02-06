import logging
from flask import Flask, request, Response, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import *
from exceptions import NewMessagesReceived
from twilio_services import send_message_twilio
from flask_cors import CORS
import sentry_sdk
import os
from dotenv import load_dotenv
from email_services import send_email

load_dotenv()

sentry_sdk.init(
    environment=os.getenv("SENTRY_ENVIRONMENT"),
    dsn=os.getenv("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
CORS(app, origins=["https://rover-landing-page.vercel.app", "http://localhost:3000"])

TWILIO_NUMBER = "+13134258270"
CONNER_NUMBER = "+18013896501"


@app.route("/bot", methods=["POST"])
async def bot():
    """
    Main endpoint for the bot. This is the endpoint that Twilio
    will call when a user sends a message to the bot.

    Returns:
        _type_: A response object
    """
    try:
        incoming_msg = request.values["Body"]
        sender_number = request.values["From"]
        twilio_number = request.values["To"]
        await async_helper(incoming_msg, sender_number, twilio_number)
        return Response(status=204)
    except NewMessagesReceived as e:
        return Response(status=204)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


async def async_helper(question, sender_number, twilio_number):
    answer = bot_logic(question, sender_number, twilio_number)
    await send_message_twilio(answer, sender_number, twilio_number)


@app.route("/devbot", methods=["POST"])
def devbot():
    """
    An endpoint for testing the bot locally

    Returns:
        _type_: A response object
    """
    try:
        data = request.get_json()
        question = data["question"]
        sender_phone_number = data["sender_phone_number"]
        twilio_number = data["twilio_phone_number"]
        answer = bot_logic(question, sender_phone_number, twilio_number)
        response = jsonify({"answer": answer})
        response.status_code = 200
        return response
    except NewMessagesReceived as e:
        return Response(status=204)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


@app.route("/backup", methods=["GET"])
def backup():
    """
    An endpoint for webhooks when the bot has an error for Twilio

    Returns:
        _type_: A response object
    """
    try:
        response = MessagingResponse()
        response.message("Sorry, there was an error on our end 😢")
        return str(response)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


@app.route("/greeting", methods=["GET"])
async def greeting():
    """
    An endpoint for a webhooks to hit when there is a missed call
    to the Twilio number, thus initiating the conversation

    Returns:
        _type_: A response object
    """
    try:
        sender_number = request.values["From"]
        twilio_number = request.values["To"]
        await send_message_twilio(
            "Hello, sorry we missed your call. How can I help you?",
            sender_number,
            twilio_number,
        )

        # TODO: Function for handling missed call logic

        response = VoiceResponse()
        response.hangup()
        return str(response)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


@app.route("/missedCall", methods=["POST"])
def missedCall():
    """An endpoint for the RingCentral webhook to hit when there is a missed call

    Returns:
        _type_: A response object
    """
    try:
        validation_token = request.headers.get("Validation-Token")
        print(f"Received validation token: {validation_token}")

        app.logger.debug("request: %s", request)
        app.logger.debug("request: %s", request.headers)

        headers = request.headers
        body = "No headers"
        if headers:
            body = headers["uuid"]

        # TODO: Function for handling missed call logic
        subject = "Missed Call to Banner PC"
        sender = "conner@textrover.co"
        recipients = ["cjvigil@live.com"]
        send_email(subject, body, sender, recipients)

        return Response(status=200, headers={"Validation-Token": validation_token})
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


@app.route("/waitlist", methods=["POST"])
def waitlist():
    """
    An endpoint for signing up for the waitlist

    Returns:
        _type_: A response object
    """
    try:
        data = request.json
        first_name = data.get("firstName", None)
        last_name = data.get("lastName", None)
        email = data.get("email", None)
        res = insert_into_waitlist(first_name, last_name, email)

        if res.data[0]:
            return Response(status=200)
        else:
            print("ERROR inserting into supabase waitlist")
            return Response(status=500)
    except Exception as e:
        print("Error:", str(e))
        sentry_sdk.capture_exception(e)
        return Response(status=500, response="An unexpected error occurred")


if __name__ == "__main__":
    app.run()
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

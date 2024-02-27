import logging
from flask import Flask, request, Response, jsonify
import requests
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import *
from exceptions import NewMessagesReceived
from twilio_services import send_message_twilio
from flask_cors import CORS
import sentry_sdk
import os
from dotenv import load_dotenv
from db_services import get_company_by_phone_number

load_dotenv()

sentry_sdk.init(
    environment=os.getenv("SENTRY_ENVIRONMENT"),
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
CORS(
    app,
    origins=[
        "https://rover-landing-page.vercel.app",
        "http://localhost:3000",
        "https://www.textrover.co",
    ],
)

TWILIO_NUMBER_TEST = "+13134258270"
TWILIO_NUMBER_BANNERPC = "+16503003890"


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
        sender_phone_number = request.values["From"]
        twilio_number = request.values["To"]

        if not check_company_hours(twilio_number):
            return Response(status=204)

        await async_helper(incoming_msg, sender_phone_number, twilio_number)
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

        if not check_company_hours(twilio_number):
            return Response(status=204)

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


@app.route("/voice", methods=["GET", "POST"])
async def voice():
    """
    An endpoint for a webhooks to hit when there is a missed call
    to the Twilio number, thus initiating the conversation

    Returns:
        _type_: A response object
    """
    try:
        sender_number = request.values["From"]
        twilio_number = request.values["To"]
        call_sid = request.values["CallSid"]
        company_name = ""

        if not check_company_hours(twilio_number):
            response = VoiceResponse()
            return str(response)

        company_result = get_company_by_phone_number(twilio_number)
        if company_result.data:
            company_name = company_result.data[0]["name"]

        response = VoiceResponse()
        response.say(
            f"Thanks for calling {company_name}. Please leave a message after the beep."
        )

        response.record(
            maxLength="60",
            recording_status_callback="/handle-voicemail-download",
            recording_status_callback_event="completed",
            # transcribe_callback="/handle-transcription",
        )

        if request.method == "POST":
            await missed_call_logic(twilio_number, sender_number, call_sid)

        return str(response)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


# https://guarded-fjord-24910-40caeb8e0ba2.herokuapp.com/voice


@app.route("/handle-voicemail-download", methods=["POST"])
def handle_voicemail_download():
    recording_url_twilio = request.form["RecordingUrl"]
    recording_sid = request.form["RecordingSid"]
    call_sid = request.form["CallSid"]

    try:
        response = requests.get(recording_url_twilio)

        if response.status_code == 200:
            filename = f"{recording_sid}.wav"
            recording_url_supabase = upload_to_supabase(
                response.content, "voicemail-recordings", filename
            )
            add_voicemail_info_to_missed_call(
                call_sid, recording_sid, recording_url_supabase
            )
        else:
            print(f"Failed to download recording. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error: {str(e)}")

    return "", 204


@app.route("/handle-transcription", methods=["POST"])
def handle_transcription():
    sender_number = request.values["From"]
    twilio_number = request.values["To"]
    transcription_sid = request.form["TranscriptionSid"]
    transcription_text = request.form["TranscriptionText"]
    transcription_status = request.form["TranscriptionStatus"]
    transcription_url = request.form["TranscriptionUrl"]
    recording_sid = request.form["RecordingSid"]
    recording_url = request.form["RecordingUrl"]
    call_sid = request.form["CallSid"]

    print(f"Transcription: {transcription_text}")

    # Add transcription to recording in database

    return "", 204


@app.route("/missedCall", methods=["POST"])
async def missedCall():
    """An endpoint for the RingCentral webhook to hit when there is a missed call FOR BANNERPC

    Returns:
        _type_: A response object
    """
    try:
        validation_token = request.headers.get("Validation-Token")
        content_length = int(request.headers["content-length"])

        if content_length == 0:
            return Response(status=200, headers={"Validation-Token": validation_token})

        request_json = json.loads(request.data.decode("utf-8"))
        to_phone_number = request_json["body"]["parties"][0]["to"]["phoneNumber"]
        to_phone_number = TWILIO_NUMBER_BANNERPC  # TEMPORARY FIX FOR BANNERPC
        from_phone_number = request_json["body"]["parties"][0]["from"]["phoneNumber"]

        if not check_company_hours(to_phone_number):
            return Response(status=204)

        await missed_call_logic(to_phone_number, from_phone_number)

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

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
from clients import twilio_client

load_dotenv()

sentry_sdk.init(
    environment=os.getenv("SENTRY_ENVIRONMENT"),
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
CORS(app, origins=["https://rover-landing-page.vercel.app", "http://localhost:3000"])

TWILIO_NUMBER = "+13134258270"


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

        if not check_company_hours(twilio_number):
            response = VoiceResponse()
            return str(response)

        await missed_call_logic(twilio_number, sender_number)
        response = VoiceResponse()

        # response.play(
        #     "https://rdlrwjmixecxtaqxvxne.supabase.co/storage/v1/object/public/voicemail%20recordings/firstwavetest.wav"
        # )
        # response.say("Please leave a message after the beep.")

        # response.record(
        #     action="/handle-recording",  # URL to handle the recorded voicemail
        #     maxLength="60",  # Maximum length of the voicemail in seconds
        #     # transcribe="true",  # Enable transcription of the voicemail
        #     # transcribeCallback="/handle-transcription",  # URL to handle transcription callback
        #     # recording_status_callback="/handle-voicemail-download",
        #     # recording_status_callback_event="completed",
        # )

        return str(response)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Unexpected error: {e}")
        return jsonify(error="Internal Server Error"), 500


@app.route("/missedCall", methods=["POST"])
async def missedCall():
    """An endpoint for the RingCentral webhook to hit when there is a missed call

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
        to_phone_number = TWILIO_NUMBER  # TEMPORARY FIX FOR TODAY
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


# @app.route("/voice", methods=["GET", "POST"])
# def voice():
#     sender_number = request.values["From"]
#     twilio_number = request.values["To"]

#     response = VoiceResponse()

#     response.play(
#         "https://rdlrwjmixecxtaqxvxne.supabase.co/storage/v1/object/public/voicemail%20recordings/firstwavetest.wav"
#     )
#     response.say("Please leave a message after the beep.")

#     response.record(
#         action="/handle-recording",  # URL to handle the recorded voicemail
#         maxLength="60",  # Maximum length of the voicemail in seconds
#         # transcribe="true",  # Enable transcription of the voicemail
#         # transcribeCallback="/handle-transcription",  # URL to handle transcription callback
#         # recording_status_callback="/handle-voicemail-download",
#         # recording_status_callback_event="completed",
#     )

#     return str(response)


# @app.route("/handle-recording", methods=["POST"])
# def handle_recording():
#     # You can handle the recorded voicemail here, e.g., save it to a database or file
#     recording_url = request.form["RecordingUrl"]
#     recording_duration = request.form["RecordingDuration"]
#     print(f"Recorded Voicemail URL: {recording_url}")
#     print(f"Recorded Voicemail Duration: {recording_duration}")

#     # Make a request to the recording URL to download the recording
#     try:
#         # Use Twilio client to download the voicemail recording
#         response = twilio_client.http_client.request("GET", recording_url)
        
#         # Check if the request was successful (status code 200)
#         if response.status_code == 200:
#             # Save the recording to a file or process it as needed
#             with open("downloaded_recording.mp3", "wb") as f:
#                 f.write(response.content)
#             print("Voicemail downloaded successfully.")
#         else:
#             print(f"Failed to download voicemail. Status code: {response.status_code}")

#     except Exception as e:
#         print(f"Error: {str(e)}")

#     return "", 204


# @app.route("/handle-voicemail-download", methods=["POST"])
# def handle_voicemail_download():
#     recording_status = request.form["RecordingStatus"]
#     recording_url = request.form["RecordingUrl"]

#     print(f"Recording Status: {recording_status}")
#     print(f"Recording URL: {recording_url}")

#     response = requests.get(recording_url)
#     print(response)
#     print(response.content)

#     return "", 204


# @app.route("/handle-transcription", methods=["POST"])
# def handle_transcription():
#     # You can handle the transcription of the voicemail here
#     transcription_text = request.form["TranscriptionText"]
#     print(f"Transcription: {transcription_text}")

#     # Add your own logic to handle the transcription data
#     return "", 204


if __name__ == "__main__":
    app.run()
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

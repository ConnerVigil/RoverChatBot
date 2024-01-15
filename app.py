from flask import Flask, request, Response, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import askgpt, retrieve_current_conversation
from twilio_services import send_message
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/bot", methods=["POST"])
async def bot():
    """
    Main function for the bot. This is the function that Twilio
    will call when a user sends a message to the bot.

    Returns:
        _type_: A response object
    """
    incoming_msg = request.values["Body"]
    sender_number = request.values["From"]
    twilio_number = request.values["To"]
    await async_helper(incoming_msg, sender_number, twilio_number)
    return Response(status=204)


async def async_helper(question, sender_number, twilio_number):
    user_id, conversation_id, chat_log = retrieve_current_conversation(sender_number)
    answer = askgpt(question, user_id, conversation_id, chat_log)
    await send_message(answer, sender_number, twilio_number)
    return


@app.route("/devbot", methods=["POST"])
def devbot():
    """
    An endpoint for testing the bot locally

    Returns:
        _type_: A response object
    """
    data = request.get_json()
    question = data["question"]
    sender_phone_number = data["phone_number"]

    user_id, conversation_id, chat_log = retrieve_current_conversation(
        sender_phone_number
    )

    answer = askgpt(question, user_id, conversation_id, chat_log)
    response = jsonify({"answer": answer})
    response.status_code = 200
    return response


@app.route("/backup", methods=["GET"])
def backup():
    """
    An endpoint for webhooks when the bot has an error

    Returns:
        _type_: A response object
    """
    response = MessagingResponse()
    response.message("Sorry, there was an error on our end 😢")
    return str(response)


@app.route("/greeting", methods=["GET"])
async def greeting():
    """
    An endpoint for a webhooks to hit when there is a missed call,
    thus initiating the conversation

    Returns:
        _type_: A response object
    """
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


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, Response, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import *
from twilio_services import send_message_twilio
from flask_cors import CORS
import time
from db_services import insert_into_waitlist

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
    incoming_msg = request.values["Body"]
    sender_number = request.values["From"]
    twilio_number = request.values["To"]
    await async_helper(incoming_msg, sender_number, twilio_number)
    return Response(status=204)


async def async_helper(question, sender_number, twilio_number):
    user_id, conversation_id, chat_log = retrieve_current_conversation(
        sender_number, twilio_number
    )
    chat_log.append({"role": "user", "content": question})
    answer = askgpt(question, user_id, conversation_id, chat_log)
    await send_message_twilio(answer, sender_number, twilio_number)


@app.route("/devbot", methods=["POST"])
def devbot():
    """
    An endpoint for testing the bot locally

    Returns:
        _type_: A response object
    """
    data = request.get_json()
    question = data["question"]
    sender_phone_number = data["sender_phone_number"]

    user_id, conversation_id, chat_log = retrieve_current_conversation(
        sender_phone_number
    )

    if user_id is None and conversation_id is None and chat_log is None:
        return Response(status=204)

    answer = askgpt(question, user_id, conversation_id, chat_log)
    response = jsonify({"answer": answer})
    response.status_code = 200
    return response


@app.route("/devbot2", methods=["POST"])
def devbot2():
    data = request.get_json()
    question = data["question"]
    sender_phone_number = data["phone_number"]
    twilio_phone_number = data["twilio_phone_number"]

    user_id, conversation_id = register_user_and_conversation(sender_phone_number, twilio_phone_number)
    insert_message(question, "user", user_id, conversation_id)

    conversation_result = get_conversation_from_queue(conversation_id)

    if len(conversation_result.data) == 0:
        print("insert_into_conversation_queue")
        insert_into_conversation_queue(conversation_id)

    return Response(status=204)


@app.route("/processmessage", methods=["POST"])
def processmessage():
    data = request.get_json()
    conversation_queue_entry = data["record"]
    conversation_id = conversation_queue_entry["conversation_id"]
    user_id = conversation_queue_entry["user_id"]
    user_result = get_user_by_id(user_id)
    company_id = user_result.data[0]["company_id"]
    company_result = get_company_by_id(company_id)
    twilio_phone_number = company_result.data[0]["phone_number"]

    print("sleeping for 5 seconds")
    time.sleep(5)

    conversation_res = get_conversation_from_queue(conversation_id)
    if len(conversation_res.data) == 0:
        print("conversation not in queue")
        return Response(status=204)

    remove_conversation_from_queue(conversation_id)

    chat_log = initiate_chat_log_and_get_context(twilio_phone_number)
    messages = get_messages_by_conversation_id(conversation_id)
    chat_log = build_chat_log_from_conversation_history(messages, chat_log)

    question = chat_log[-1]["content"]
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
    await send_message_twilio(
        "Hello, sorry we missed your call. How can I help you?",
        sender_number,
        twilio_number,
    )
    response = VoiceResponse()
    response.hangup()
    return str(response)


@app.route("/missedCall", methods=["POST"])
async def test():
    # await send_message_twilio(
    #     f"Content-Length: {request.content_length}", CONNER_NUMBER, TWILIO_NUMBER
    # )
    # insert into supabase missed call
    try:
        validation_token = request.headers.get("Validation-Token")

        if "application/json" not in request.content_type:
            raise ValueError(
                f"Invalid Content-Type: {request.content_type}. Expected application/json."
            )

        # json_data = request.get_json()
        # if json_data is None:
        #     raise ValueError("Invalid JSON data or missing Content-Type header")

        # print(f"Received JSON data: {json_data}")

        return Response(status=200, headers={"Validation-Token": validation_token})
    except ValueError as ve:
        print(f"Error processing JSON data: {ve}")
        return jsonify(error="Bad Request"), 400
    except Exception as e:
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
        return Response(status=500, response="An unexpected error occurred")


if __name__ == "__main__":
    app.run(debug=True)

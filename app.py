from flask import Flask, request, Response, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import askgpt
from twilio_services import send_message
from flask_cors import CORS
from db_services import *

app = Flask(__name__)
CORS(app)


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


@app.route("/devbot", methods=["POST"])
def devbot():
    data = request.get_json()
    question = data["question"]
    sender_phone_number = data["phone_number"]
    bot_phone_number = "1234567890"

    # check if the phone number is registered as a user
    result = get_user_by_phone_number(sender_phone_number)

    if len(result.data) == 0:
        # if not, register the phone number as a user

        # insert new user into the db
        user_insert_result = add_user(bot_phone_number)

        # then get the user id and insert a new conversation into the db
        user_id = user_insert_result.data[0]["id"]
        conversation_insert_result = add_conversation(user_id)

        # then get the conversation id
        conversation_id = conversation_insert_result.data[0]["id"]

        # then get the context and put it into the chat log
        context_result = get_context_by_phone_number(bot_phone_number)
        chat_log = []
        if len(context_result.data) == 1:
            chat_log.append(
                {"role": "system", "content": context_result.data[0]["content"]}
            )

    elif len(result.data) == 1:
        # if yes

        # get the user id and get the most recent conversation id
        user_id = result.data[0]["id"]
        conversation_result = get_conversation_by_user_id(user_id)
        conversation_id = conversation_result.data[0]["id"]

        # get the context first and put it into the chat log
        chat_log = []
        context_result = get_context_by_phone_number(bot_phone_number)

        if len(context_result.data) == 1:
            chat_log.append(
                {"role": "system", "content": context_result.data[0]["content"]}
            )

        # then grab all the messages from that conversation and put them into chat_log
        message_result = get_messages_by_conversation_id(conversation_id)

        for message in message_result.data:
            chat_log.append({"role": message["role"], "content": message["content"]})

    else:
        print("ERROR")
        response.status_code = 500
        return response

    answer = askgpt(question, user_id, conversation_id, chat_log)
    response = jsonify({"answer": answer})
    response.status_code = 200
    return response


@app.route("/backup", methods=["GET"])
def backup():
    response = MessagingResponse()
    response.message("Sorry, there was an error on our end 😢")
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


if __name__ == "__main__":
    app.run(debug=True)

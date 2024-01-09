from flask import Flask, request, Response, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from chatbot import askgpt, send_message
import os
from dotenv import load_dotenv
from flask_cors import CORS
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL_TEST"), os.getenv("SUPABASE_KEY_TEST"))

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "Hello World!\n"


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

    result = (
        supabase.table("Users")
        .select("*")
        .eq("phone_number", sender_phone_number)
        .execute()
    )

    # check if the phone number is registered as a user
    if len(result.data) == 0:
        # if not, register the phone number as a user
        # insert new user into the db, then get the user id and insert a new
        # conversation into the db, then get the conversation id and insert a new
        # message into the db

        user_insert_result = (
            supabase.table("Users")
            .insert(
                {
                    "first_name": None,
                    "last_name": None,
                    "phone_number": sender_phone_number,
                    "email": None,
                }
            )
            .execute()
        )

        user_id = user_insert_result.data[0]["id"]

        conversation_insert_result = (
            supabase.table("Conversations").insert({"user_id": user_id}).execute()
        )

        conversation_id = conversation_insert_result.data[0]["id"]

        context_result = (
            supabase.table("Contexts")
            .select("*")
            .eq("company_phone_number", bot_phone_number)
            .execute()
        )

        chat_log = []
        if len(context_result.data) == 1:
            chat_log.append(
                {"role": "system", "content": context_result.data[0]["content"]}
            )

    elif len(result.data) == 1:
        # if yes, get the user id and get the most recent conversation id, then
        # grab all the messages from that conversation and put them into chat_log

        user_id = result.data[0]["id"]

        conversation_result = (
            supabase.table("Conversations")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at")
            .limit(1)
            .execute()
        )

        conversation_id = conversation_result.data[0]["id"]

        message_result = (
            supabase.table("Messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at")
            .execute()
        )

        chat_log = []

        # Get context first
        context_result = (
            supabase.table("Contexts")
            .select("*")
            .eq("company_phone_number", bot_phone_number)
            .execute()
        )

        if len(context_result.data) == 1:
            chat_log.append(
                {"role": "system", "content": context_result.data[0]["content"]}
            )

        # Then all the messages
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

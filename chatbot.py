import os
from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client
import json
from flask import session
from termcolor import colored
from datetime import datetime
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL_TEST"), os.getenv("SUPABASE_KEY_TEST"))

openAI_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date of the appointment",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of the appointment",
                    },
                },
                "required": ["date", "time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "End the conversation when customer is satisfied with the service",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date_and_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


def askgpt(
    question: str, user_id: str, conversation_id: str, chat_log: list = None
) -> str:
    chat_log.append({"role": "user", "content": question})

    supabase.table("Messages").insert(
        {
            "content": question,
            "role": "user",
            "user_id": user_id,
            "conversation_id": conversation_id,
        }
    ).execute()

    response = openAI_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=chat_log,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Check if the model wanted to call a function
    if tool_calls:
        available_functions = {
            "book_appointment": {
                "function": book_appointment,
                "parameters": ["date", "time"],
            },
            "end_conversation": {
                "function": end_conversation,
                "parameters": [],
            },
            "get_current_date_and_time": {
                "function": get_current_date_and_time,
                "parameters": [],
            },
        }

        # Iterate through tool_calls and restructure into json to send back to the model
        new_tool_calls = []
        for tool_call in tool_calls:
            temp = {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            new_tool_calls.append(temp)

        newMessage = {
            "role": "assistant",
            "content": None,
            "tool_calls": new_tool_calls,
        }

        # extend conversation with model's reply
        chat_log.append(newMessage)
        # choosing not to insert the tool calls into the database for now

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_info = available_functions.get(function_name)

            if function_info:
                function_to_call = function_info["function"]
                function_parameters = function_info["parameters"]

                function_args = json.loads(tool_call.function.arguments)
                function_args = {
                    param: function_args.get(param) for param in function_parameters
                }

                function_response = function_to_call(**function_args)
                chat_log.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        # get a new response from the model where it can see the function response
        second_response = openAI_client.chat.completions.create(
            model="gpt-3.5-turbo-1106", messages=chat_log
        )

        answer = second_response.choices[0].message.content
    else:
        answer = response.choices[0].message.content

    chat_log = chat_log + [{"role": "assistant", "content": answer}]

    supabase.table("Messages").insert(
        {
            "content": answer,
            "role": "assistant",
            "user_id": user_id,
            "conversation_id": conversation_id,
        }
    ).execute()

    pretty_print_conversation(chat_log)
    return answer


async def send_message(content: str, sender_number: str, twilio_number: str) -> None:
    twilio_client.messages.create(
        body=content,
        from_=twilio_number,
        to=sender_number,
    )


def book_appointment(date: str, time: str) -> str:
    print("Booking Appointment...")
    return json.dumps({"date booked": date, "time booked": time})


def end_conversation():
    session.clear()
    print("Conversation Ended")
    return json.dumps({"end conversation": True})


def get_current_date_and_time() -> str:
    current_date_time = datetime.now()
    return current_date_time.isoformat()


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }

    for message in messages:
        if message["role"] == "system":
            # print(
            #     colored(
            #         f"system: {message['content']}\n", role_to_color[message["role"]]
            #     )
            # )
            continue
        elif message["role"] == "user":
            print(
                colored(f"user: {message['content']}\n", role_to_color[message["role"]])
            )
        elif message["role"] == "assistant" and message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['function_call']}\n",
                    role_to_color[message["role"]],
                )
            )
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "tool":
            print(
                colored(
                    f"function ({message['name']}): {message['content']}\n",
                    role_to_color[message["role"]],
                )
            )

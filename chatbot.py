import json
import time
from datetime import time as time2, timedelta
from exceptions import NewMessagesReceived
from termcolor import colored
from openai_functions import tools, available_functions
from db_services import *
from openai_services import *
from clients import environment
from twilio_services import send_message_twilio

CHATGPT_MODEL = "gpt-3.5-turbo-1106"
RESPONSE_SLEEP_TIME = 5


def bot_logic(question: str, sender_phone_number: str, twilio_number: str) -> str:
    """
    The main logic of the bot

    Args:
        question (str): The question to ask the bot
        sender_phone_number (str): The phone number of the sender
        twilio_number (str): The phone number of the company

    Raises:
        NewMessagesReceived: Need to respond to more messages

    Returns:
        str: The answer from the bot
    """
    company_result = get_company_by_phone_number(twilio_number)
    company_id = company_result.data[0]["id"]
    user = get_user_if_exists_or_create_new_user(sender_phone_number, company_id)
    user_id = user["id"]
    conversation = get_conversation_if_exists_or_create_new_conversation(user_id)
    conversation_id = conversation["id"]

    message_insert_result = insert_message(
        content=question, role="user", conversation_id=conversation_id
    )

    time.sleep(RESPONSE_SLEEP_TIME)
    chat_log = get_chat_log(conversation_id, twilio_number)

    if chat_log[-1]["id"] != message_insert_result.data[0]["id"]:
        raise NewMessagesReceived("Need to respond to more messages")

    chat_log = filter_out_id_from_chat_log(chat_log)
    answer = askgpt(user_id, conversation_id, chat_log)
    chat_log.append({"role": "assistant", "content": answer})

    if environment == "development":
        print_chat_log_without_context(chat_log)

    return answer


def askgpt(user_id: str, conversation_id: str, chat_log: list) -> str:
    """
    Ask the GPT-3 model a question

    Args:
        user_id (str): The id of the user
        conversation_id (str): The id of the conversation
        chat_log (list, optional): The history of the conversation

    Returns:
        str: The answer from the model
    """

    response = create_gpt_response(
        model=CHATGPT_MODEL,
        messages=chat_log,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Check if the model wanted to call a function
    if tool_calls:
        # Iterate through tool_calls and restructure into json to send back to the model
        new_tool_calls = []
        for tool_call in tool_calls:
            new_tool_calls.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            )

        # extend conversation with model's reply
        chat_log.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": new_tool_calls,
            }
        )

        # insert the tool call into the db as a message
        insert_message(
            content=None,
            role="assistant",
            conversation_id=conversation_id,
            tool_calls=new_tool_calls,
        )

        # insert all tool calls into the db and chat log
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

                if function_name == "save_customers_personal_information":
                    function_args["phone_number"] = get_user_by_id(user_id).data[0][
                        "phone_number"
                    ]

                function_response = function_to_call(**function_args)
                chat_log.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

                insert_message(
                    content=function_response,
                    role="tool",
                    conversation_id=conversation_id,
                    tool_call_id=tool_call.id,
                    function_name=function_name,
                )

        # get a new response from the model where it can see the function response
        second_response = create_gpt_response(
            model=CHATGPT_MODEL, messages=chat_log, tool_choice="none"
        )
        answer = second_response.choices[0].message.content

    else:
        answer = response.choices[0].message.content

    chat_log = chat_log + [{"role": "assistant", "content": answer}]
    insert_message(
        content=answer,
        role="assistant",
        conversation_id=conversation_id,
    )

    return answer


async def missed_call_logic(to_phone_number: str, from_phone_number: str):
    """
    The logic for when a missed call is received

    Args:
        to_phone_number (str): The phone number the call was made to
        from_phone_number (str): The phone number the call was made from
    """
    company_result = get_company_by_phone_number(to_phone_number)
    company_id = None
    if len(company_result.data) == 1:
        company_id = company_result.data[0]["id"]

    user = get_user_if_exists_or_create_new_user(from_phone_number, company_id)
    conversation = get_conversation_if_exists_or_create_new_conversation(user["id"])
    conversation_id = conversation["id"]

    company_result = get_company_by_phone_number(to_phone_number)
    if len(company_result.data) == 1:
        company_name = company_result.data[0]["name"]
        message = f"Hello, welcome to {company_name}. Sorry, we missed your call. How can I help you?"
    else:
        message = "Hello, sorry we missed your call. How can I help you?"

    await send_message_twilio(
        content=message,
        receiving_number=from_phone_number,
        sending_number=to_phone_number,
    )
    insert_message(message, "assistant", conversation_id)
    insert_into_missed_calls(to_phone_number, from_phone_number, conversation_id)


def get_user_if_exists_or_create_new_user(phone_number: str, company_id: str = None):
    """
    Get the user if it exists, or create a new user

    Args:
        phone_number (str): The phone number of the user
        company_id (str, optional): The id of the company that the user is messaging. Defaults to None.

    Returns:
        _type_: The user object
    """
    user_result = get_user_by_phone_number(phone_number)
    if not user_result.data:
        user_insert_result = insert_user(phone_number, company_id)
        user = user_insert_result.data[0]
    else:
        user = user_result.data[0]
    return user


def get_conversation_if_exists_or_create_new_conversation(user_id: str):
    """
    Get the conversation if it exists, or create a new conversation

    Args:
        user_id (str): The id of the user

    Returns:
        _type_: The conversation object
    """
    conversation_result = get_conversation_by_user_id(user_id)
    if not conversation_result.data:
        conversation_insert_result = insert_conversation(user_id)
        conversation = conversation_insert_result.data[0]
    else:
        if check_if_conversation_is_active(conversation_result.data[0]["id"]):
            conversation = conversation_result.data[0]
        else:
            conversation_insert_result = insert_conversation(user_id)
            conversation = conversation_insert_result.data[0]

    return conversation


def get_chat_log(conversation_id: str, twilio_phone_number: str) -> list:
    """
    Gets the chat log from the conversation

    Args:
        conversation_id (str): The id of the conversation
        twilio_phone_number (str): The phone number of the company

    Returns:
        list: The chat log
    """
    chat_log = initiate_chat_log_and_get_context(twilio_phone_number)
    messages_result = get_messages_by_conversation_id(conversation_id)
    chat_log = build_chat_log_from_conversation_history(messages_result.data, chat_log)
    return chat_log


def initiate_chat_log_and_get_context(company_phone_number: str) -> list:
    """
    Initiates the chat log and gets the context of the company

    Args:
        sender_phone_number (str): The phone number of the sender

    Returns:
        _type_: The chat log
    """
    chat_log = []
    company_result = get_company_by_phone_number(company_phone_number)

    if len(company_result.data) == 1:
        chat_log.append(
            {"role": "system", "content": company_result.data[0]["context"]}
        )
    return chat_log


def build_chat_log_from_conversation_history(messages: list, chat_log: list) -> str:
    """
    Builds a chat log from the conversation history

    Args:
        messages (list): The conversation history

    Returns:
        str: The finished chat log
    """
    for message in messages:
        new_message = {
            "role": message["role"],
            "content": message["content"],
            "id": message["id"],
        }

        if message["tool_calls"] != []:
            new_message["tool_calls"] = message["tool_calls"]

        if message["tool_call_id"] != None:
            new_message["tool_call_id"] = message["tool_call_id"]

        if message["function_name"] != None:
            new_message["name"] = message["function_name"]

        chat_log.append(new_message)

    return chat_log


def filter_out_id_from_chat_log(chat_log: list) -> list:
    """
    Filters out the id from the chat log

    Args:
        chat_log (list): The chat log to filter

    Returns:
        list: The filtered chat log
    """
    for message in chat_log:
        message.pop("id", None)
    return chat_log


def check_company_hours(twilio_number: str):
    """
    Check if the bot should respond for the company

    Args:
        twilio_number (str): The phone number of the company

    Returns:
        bool: True if bot should respond, False if not
    """
    company_result = get_company_by_phone_number(twilio_number)
    if len(company_result.data) == 1:
        company = company_result.data[0]
        open_time_str = company["open_time_utc"]
        close_time_str = company["close_time_utc"]
        
        open_time_timetz = datetime.strptime(open_time_str, '%H:%M:%S').time()
        close_time_timetz = datetime.strptime(close_time_str, '%H:%M:%S').time()

        current_datetime_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
        open_datetime = datetime.combine(current_datetime_utc.date(), open_time_timetz)
        close_datetime = datetime.combine(current_datetime_utc.date(), close_time_timetz)

        current_datetime_naive = current_datetime_utc.astimezone(timezone.utc).replace(tzinfo=None)

        if open_datetime > close_datetime:
            close_datetime = close_datetime + timedelta(days=1)

        if open_datetime < current_datetime_naive < close_datetime:
            return False
        else:
            return True

    return False


def print_chat_log_without_context(chat_log: list):
    """
    Prints the chat log without the context for debugging purposes

    Args:
        chat_log (list): The chat log to print
    """
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }

    for message in chat_log:
        if message["role"] == "system":
            print(colored("context", role_to_color["system"]))
            continue
        print(colored(message, role_to_color[message["role"]]))

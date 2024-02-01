import json
import time
from exceptions import NewMessagesReceived
from termcolor import colored
from openai_functions import tools, available_functions
from db_services import *
from openai_services import *
from clients import environment

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
    user_id, conversation_id = retrieve_current_conversation(
        sender_phone_number, twilio_number
    )

    message_insert_result = insert_message(
        content=question, role="user", user_id=user_id, conversation_id=conversation_id
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
            user_id=user_id,
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
                    user_id=user_id,
                    conversation_id=conversation_id,
                    tool_call_id=tool_call.id,
                    function_name=function_name,
                )

        # get a new response from the model where it can see the function response
        second_response = create_gpt_response(model=CHATGPT_MODEL, messages=chat_log)
        answer = second_response.choices[0].message.content

    else:
        answer = response.choices[0].message.content

    chat_log = chat_log + [{"role": "assistant", "content": answer}]
    insert_message(
        content=answer,
        role="assistant",
        user_id=user_id,
        conversation_id=conversation_id,
    )

    return answer


def retrieve_current_conversation(
    sender_phone_number: str, twilio_phone_number: str
) -> list:
    """
    Retrieves the current conversation

    Args:
        sender_phone_number (str): The phone number of the sender
        twilio_phone_number (str): The phone number of the company

    Raises:
        Exception: More than one user with the same phone number

    Returns:
        list: A list containing the user id and conversation id
    """
    result = get_user_by_phone_number(sender_phone_number)

    if len(result.data) == 0:
        user_id, conversation_id = register_user_and_conversation(
            sender_phone_number, twilio_phone_number
        )
    elif len(result.data) == 1:
        user_id = result.data[0]["id"]
        conversation_id = get_conversation_id_of_existing_user(user_id)
    else:
        raise Exception("More than one user with the same phone number")

    return user_id, conversation_id


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


def register_user_and_conversation(
    sender_phone_number: str, twilio_phone_number: str
) -> list:
    """
    Registers a user and conversation

    Args:
        sender_phone_number (str): The phone number of the sender
        twilio_phone_number (str): The phone number of the company

    Returns:
        list: A list containing the user id and conversation id
    """
    company_result = get_company_by_phone_number(twilio_phone_number)

    if len(company_result.data) == 1:
        company_id = company_result.data[0]["id"]
        user_insert_result = insert_user(sender_phone_number, company_id)
    else:
        user_insert_result = insert_user(sender_phone_number)

    user_id = user_insert_result.data[0]["id"]
    conversation_insert_result = insert_conversation(user_id)
    conversation_id = conversation_insert_result.data[0]["id"]
    return user_id, conversation_id


def get_conversation_id_of_existing_user(user_id: str) -> list:
    """Get the conversation id of an existing user, checking if the conversation is active

    Args:
        user_id (str): The id of the user

    Returns:
        list: The conversation id
    """
    conversation_result = get_conversation_by_user_id(user_id)
    conversation_id = conversation_result.data[0]["id"]

    if not check_if_conversation_is_active(conversation_id):
        conversation_insert_result = insert_conversation(user_id)
        conversation_id = conversation_insert_result.data[0]["id"]

    return conversation_id


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


def get_conversation_id_by_phone_number(sender_phone_number: str) -> str:
    """
    Gets the conversation id by the phone number

    Args:
        sender_phone_number (str): The phone number of the sender

    Returns:
        str: The conversation id, or None if there is no conversation
    """
    result = get_user_by_phone_number(sender_phone_number)

    if len(result.data) == 1:
        user_id = result.data[0]["id"]
        conversation_result = get_conversation_by_user_id(user_id)
        conversation_id = conversation_result.data[0]["id"]
        return conversation_id
    else:
        print(f"ERROR - no user with the phone number: {sender_phone_number}")
        return None


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


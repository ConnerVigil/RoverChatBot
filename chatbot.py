import json
from termcolor import colored
from openai_functions import tools, available_functions
from db_services import *
from clients import openAI_client


def askgpt(
    question: str, user_id: str, conversation_id: str, chat_log: list = None
) -> str:
    """
    Ask the GPT-3 model a question

    Args:
        question (str): The question to ask the model
        user_id (str): The id of the user
        conversation_id (str): The id of the conversation
        chat_log (list, optional): The history of the conversation. Defaults to None.

    Returns:
        str: The answer from the model
    """
    chat_log.append({"role": "user", "content": question})
    add_message(question, "user", user_id, conversation_id)

    response = openAI_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=chat_log,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    print(tool_calls)

    # Check if the model wanted to call a function
    if tool_calls:
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

        # insert the tool call into the db as a message
        # add_message(None, "assistant", user_id, conversation_id)

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
                    function_args["phone_number"] = get_user_by_id(user_id).data[0]["phone_number"]

                function_response = function_to_call(**function_args)
                chat_log.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                add_message(function_response, "tool", user_id, conversation_id)

        print(chat_log)
        # get a new response from the model where it can see the function response
        second_response = openAI_client.chat.completions.create(
            model="gpt-3.5-turbo-1106", messages=chat_log
        )

        answer = second_response.choices[0].message.content
    else:
        answer = response.choices[0].message.content

    chat_log = chat_log + [{"role": "assistant", "content": answer}]
    add_message(answer, "assistant", user_id, conversation_id)
    pretty_print_conversation(chat_log)
    return answer


def retrieve_current_conversation(sender_phone_number: str) -> list:
    """
    Retrieves all the information needed to continue a conversation

    Args:
        sender_phone_number (str): The phone number of the sender

    Returns:
        list: A list containing the user id, conversation id, and chat log
    """
    # check if the phone number is registered as a user
    result = get_user_by_phone_number(sender_phone_number)

    if len(result.data) == 0:
        # if not, register the phone number as a user

        # insert new user into the db
        user_insert_result = add_user(sender_phone_number)

        # then get the user id and insert a new conversation into the db
        user_id = user_insert_result.data[0]["id"]
        conversation_insert_result = add_conversation(user_id)

        # then get the conversation id
        conversation_id = conversation_insert_result.data[0]["id"]

        # then get the context and put it into the chat log
        context_result = get_context_by_phone_number(sender_phone_number)
        chat_log = []
        if len(context_result.data) == 1:
            chat_log.append(
                {"role": "system", "content": context_result.data[0]["content"]}
            )
    elif len(result.data) == 1:
        # if yes, check if there is an active conversation

        # get the user id and get the most recent conversation id
        user_id = result.data[0]["id"]
        conversation_result = get_conversation_by_user_id(user_id)
        conversation_id = conversation_result.data[0]["id"]

        if not check_if_conversation_is_active(conversation_id):
            # if not, insert a new conversation into the db
            conversation_insert_result = add_conversation(user_id)
            conversation_id = conversation_insert_result.data[0]["id"]

        # get the context first and put it into the chat log
        chat_log = []
        context_result = get_context_by_phone_number(sender_phone_number)

        if len(context_result.data) == 1:
            chat_log.append(
                {"role": "system", "content": context_result.data[0]["content"]}
            )

        # then grab all the messages from that conversation and put them into chat_log
        message_result = get_messages_by_conversation_id(conversation_id)

        for message in message_result.data:
            chat_log.append({"role": message["role"], "content": message["content"]})

    else:
        print("ERROR - more than one user with the same phone number")
        return []

    return user_id, conversation_id, chat_log


def pretty_print_conversation(messages):
    """
    Prints the conversation in a pretty format

    Args:
        messages (_type_): The messages to print
    """
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

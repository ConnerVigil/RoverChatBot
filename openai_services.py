from clients import openAI_client
from termcolor import colored
from clients import environment


def create_gpt_response(model: str, messages: list, tools: list, tool_choice: str):
    """
    Uses the Open AI client to make a response with the conversation so far and other parameters.

    Args:
        model (str): model of ChatGPT
        messages (list): the conversation up to that point.
        tools (list): Allows for function calling.
        tool_choice (str): "auto" allows the model to call the function if it wants. "none" (THE STRING) prohibits the model from calling a function.

    Returns:
        _type_: The response from the OpenAI client
    """
    response = openAI_client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
    )

    if environment == "development":
        print(
            colored(
                f"Token count for current conversation: {response.usage.total_tokens}",
                "green",
            )
        )

    return response

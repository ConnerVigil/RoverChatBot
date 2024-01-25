from clients import openai_client

def create_gpt_response(model, messages, tools=None, tool_choice=None):
    """Uses the Open AI client to make a response with the conversation so far and other parameters. 

    Args:
        model (_type_): model of ChatGPT
        messages (_type_): the conversation up to that point. 
        tools (_type_, optional): _description_. Allows for function calling. 
        tool_choice (_type_, optional): _description_. "auto" allows the model to call the function if it wants. "none" (THE STRING) prohibits the model from calling a function. 

    Returns:
        _type_: _description_
    """
    if tools is None and tool_choice is None:
        return openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
    return openai_client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
    ) 

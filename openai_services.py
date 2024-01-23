from clients import openai_client

def create_gpt_response(model, messages, tools=None, tool_choice=None):
    "takes named arguments and returns the response that GPT creates"
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

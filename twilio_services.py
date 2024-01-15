from clients import twilio_client


async def send_message(content: str, sender_number: str, twilio_number: str) -> None:
    """
    Sends a text message to a user

    Args:
        content (str): The message to be sent
        sender_number (str): The phone number receiving the message
        twilio_number (str): The phone number sending the message
    """
    twilio_client.messages.create(
        body=content,
        from_=twilio_number,
        to=sender_number,
    )

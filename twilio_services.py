from clients import twilio_client


async def send_message(
    content: str, receiving_number: str, sending_number: str
) -> None:
    """
    Sends a text message to a user

    Args:
        content (str): The message to be sent
        receiving_number (str): The phone number receiving the message
        sending_number (str): The phone number sending the message
    """
    twilio_client.messages.create(
        body=content,
        from_=sending_number,
        to=receiving_number,
    )

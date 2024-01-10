from clients import twilio_client


async def send_message(content: str, sender_number: str, twilio_number: str) -> None:
    twilio_client.messages.create(
        body=content,
        from_=twilio_number,
        to=sender_number,
    )

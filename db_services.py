from clients import supabase
from datetime import datetime, timezone

SECONDS_FOR_CONVERSATION_TO_BE_INACTIVE = 1 * 24 * 60 * 60


def get_user_by_phone_number(phone_number: str):
    """
    Get a user by phone number from the database

    Args:
        phone_number (str): The phone number of the user

    Returns:
        _type_: The result of the query
    """
    res = supabase.table("Users").select("*").eq("phone_number", phone_number).execute()
    return res


def get_user_by_id(user_id: str):
    """
    Get a user by id from the database

    Args:
        user_id (str): The id of the user

    Returns:
        _type_: The result of the query
    """
    res = supabase.table("Users").select("*").eq("id", user_id).execute()
    return res


def get_user_by_email(email: str):
    """
    Get a user by email from the database

    Args:
        email (str): The email of the user

    Returns:
        _type_: The result of the query
    """
    res = supabase.table("Users").select("*").eq("email", email).execute()
    return res


def insert_user(phone_number: str, company_id: str = None):
    """
    Insert a user into the database

    Args:
        phone_number (str): The phone number of the user
        company_id (str, optional): The id of the company. Defaults to None.

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Users")
        .insert({"phone_number": phone_number, "company_id": company_id})
        .execute()
    )
    return res


def update_user(
    phone_number: str, first_name: str = None, last_name: str = None, email: str = None
):
    """
    Update a user in the database

    Args:
        phone_number (str): The phone number of the user
        first_name (str, optional): The first name of the user. Defaults to None.
        last_name (str, optional): The last name of the user. Defaults to None.
        email (str, optional): The email of the user. Defaults to None.

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Users")
        .update(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            }
        )
        .eq("phone_number", phone_number)
        .execute()
    )
    return res


def get_company_by_id(company_id: str):
    """
    Get a company by id from the database

    Args:
        company_id (str): The id of the company

    Returns:
        _type_: The result of the query
    """
    res = supabase.table("Companies").select("*").eq("id", company_id).execute()
    return res


def get_company_by_phone_number(phone_number: str):
    """
    Get a company by phone number from the database

    Args:
        phone_number (str): The phone number of the user

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Companies")
        .select("*")
        .eq("phone_number", phone_number)
        .execute()
    )
    return res


def insert_conversation(user_id: str):
    """
    Insert a conversation into the database

    Args:
        user_id (str): The id of the user

    Returns:
        _type_: The result of the query
    """
    res = supabase.table("Conversations").insert({"user_id": user_id}).execute()
    return res


def get_conversation_by_id(conversation_id: str):
    """
    Get a conversation by id from the database

    Args:
        conversation_id (str): The id of the conversation

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Conversations").select("*").eq("id", conversation_id).execute()
    )
    return res


def get_conversation_by_user_id(user_id: str):
    """
    Get the most recent conversation by user id from the database

    Args:
        user_id (str): The id of the user

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at")
        .limit(1)
        .execute()
    )
    return res


def get_messages_by_conversation_id(conversation_id: str):
    """
    Get all messages by conversation id from the database

    Args:
        conversation_id (str): The id of the conversation

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return res


def insert_message(
    content: str,
    role: str,
    conversation_id: str,
    tool_calls: list = [],
    tool_call_id: str = None,
    function_name: str = None,
):
    """
    Insert a message into the database

    Args:
        content (str): Content of the message
        role (str): Role of the user who sent the message
        conversation_id (str): The id of the conversation
        tool_calls (list, optional): A list of new tool calls. Defaults to None.
        tool_call_id (str, optional): The id of the tool call. Defaults to None.
        function_name (str, optional): The name of the function called as a tool. Defaults to None.

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Messages")
        .insert(
            {
                "content": content,
                "role": role,
                "conversation_id": conversation_id,
                "tool_calls": tool_calls,
                "tool_call_id": tool_call_id,
                "function_name": function_name,
            }
        )
        .execute()
    )
    return res


def check_if_conversation_is_active(conversation_id: str) -> bool:
    """
    Uses the conversation id to check if the conversation is active.
    Inactive conversations are conversations in which at least 1 day has
    passed since the last message was sent.

    Args:
        conversation_id (str): The id of the conversation

    Returns:
        bool: True if there is an active conversation, False if there is not
    """
    res = (
        supabase.table("Messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .limit(1)
        .execute()
    )

    if len(res.data) == 0:
        return False

    last_message = res.data[0]

    current_timestamp = datetime.now(timezone.utc)
    time_difference = current_timestamp - datetime.fromisoformat(
        last_message["created_at"]
    )

    if time_difference.seconds < SECONDS_FOR_CONVERSATION_TO_BE_INACTIVE:
        return True
    else:
        return False


def insert_into_waitlist(first_name: str, last_name: str, email: str):
    """
    Insert a user into the waitlist

    Args:
        first_name (str): The first name of the user
        last_name (str): The last name of the user
        email (str): The email of the user

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Waitlist")
        .insert({"first_name": first_name, "last_name": last_name, "email": email})
        .execute()
    )
    return res


def insert_into_missed_calls(
    to_phone_number: str, from_phone_number: str, conversation_id: str = None
):
    """
    Insert a missed call into the database

    Args:
        to_phone_number (str): The phone number that was called
        from_phone_number (str): The phone number that called
        conversation_id (str, optional): The id of the conversation

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Missed_Calls")
        .insert(
            {
                "to_phone_number": to_phone_number,
                "from_phone_number": from_phone_number,
                "conversation_id": conversation_id,
            }
        )
        .execute()
    )
    return res


def get_missed_call_by_phone_number(phone_number: str):
    """
    Get a missed call by phone number from the database

    Args:
        phone_number (str): The phone number of the missed call

    Returns:
        _type_: The result of the query
    """
    res = (
        supabase.table("Missed_Calls")
        .select("*")
        .eq("from_phone_number", phone_number)
        .order("created_at")
        .limit(1)
        .execute()
    )
    return res

from clients import supabase


def get_user_by_phone_number(phone_number: str):
    """
    Get a user by phone number from the database
    """
    res = supabase.table("Users").select("*").eq("phone_number", phone_number).execute()
    return res


def add_user(
    phone_number: str, first_name: str = None, last_name: str = None, email: str = None
):
    """
    Insert a user into the database
    """
    res = (
        supabase.table("Users")
        .insert(
            {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "email": email,
            }
        )
        .execute()
    )
    return res


def get_context_by_phone_number(phone_number: str):
    """
    Get a context by phone number from the database
    """
    res = (
        supabase.table("Contexts")
        .select("*")
        .eq("company_phone_number", phone_number)
        .execute()
    )
    return res


def add_conversation(user_id: str):
    """
    Insert a conversation into the database
    """
    res = supabase.table("Conversations").insert({"user_id": user_id}).execute()
    return res


def get_conversation_by_user_id(user_id: str):
    """
    Get the most recent conversation for a user by user id from the database
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
    Get a list of messages by conversation id from the database
    """
    res = (
        supabase.table("Messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return res


def add_message(content: str, role: str, user_id: str, conversation_id: str):
    """
    Insert a message into the database
    """
    res = (
        supabase.table("Messages")
        .insert(
            {
                "content": content,
                "role": role,
                "user_id": user_id,
                "conversation_id": conversation_id,
            }
        )
        .execute()
    )
    return res

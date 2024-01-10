tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date of the appointment",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of the appointment",
                    },
                },
                "required": ["date", "time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "End the conversation when customer is satisfied with the service",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date_and_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

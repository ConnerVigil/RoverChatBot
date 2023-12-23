import os
from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client
import json
from flask import session
from termcolor import colored
from datetime import datetime

load_dotenv()

openAI_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

context = """
You are a helpful assistant for Banner Pest Services. Customers will ask you questions
about the below information and you will need to answer. If a customer asks you to book, make up a 
fake appointment timeslot for experimental purposes. Your responses need to be friendly, concise, 
and conversational. You are the customer’s best friend. Use questions at the end of each message to 
drive customers to book. Don't make assumptions about what values to plug into functions. Ask for 
clarification if a user request is ambiguous.

Serving the San Francisco Bay and East Bay Area, Banner Pest Services provides residential
and commercial pest control services. As the leading provider of eco-friendly services in
our area, we are dedicated to providing a better service for our customers. To see if we
work in your area, please check the list below, then contact us for your free estimate.

Cities serviced by Banner:
San Jose
Los Gatos
Saratoga
Campbell
Santa Clara
Cupertino
Milpitas
Alviso
Sunnyvale
Mountain View
Los Altos
Palo Alto
Menlo Park
Atherton
San Carlos
Belmont
San Mates
Burlingame
Millbrae
San Francisco
San Bruno
South San Francisco
Daly City
Brisbane
San Leandro
San Lorenzo
Castro Valley
Hayward
Union City
Fremont
Newark
Richmond
San Pablo
El Cerrito
El Sobrante
Berkeley
Albany
Oakland
Emeryville
Alameda
San Leandro
San Lorenzo
Castro Valley
Orinda
Martinez
Pinole
Hercules
Rodeo
Crockett
Port Costa
Concord
Pleasant Hill
Pittsburg
Antioch
Walnut Creek
Lafayette
Alamo
Moraga
San Ramon
Pleasanton
Danville
Diablo


Services outline

Initial Treatment

Our initial treatment usually takes the longest as we are laying all of the groundwork for
lasting protection against pests.
This treatment lasts between 30 minutes and 1 hour, is more in depth, and involves
more product than the follow up services.

30-Day Follow up

30 days following your initial treatment, your services professional will arrive to perform
your first quarterly treatment. During this treatment, we carefully examine progress, make
any needed adjustments, and break the egg cycle of any existing pests on your property.

Quarterly Treatments

After the first home pest control treatment, your committed service expert guarantees
consistent maintenance through quarter-yearly treatments planned every 90 days. These
follow-up treatments are prompt and effective, acting as crucial maintenance for your
property. Be confident that we will diligently track progress to guarantee the best
possible outcomes for you and your family!

In-depth service explanations

Granular Treatment

On each visit, our technicians use a water-activated granular treatment around the
perimeter of the house and lawn. The granules disperse into the soil, which prevents pests
from nesting close to your house.
Exterior Perimeter Treatment
Our comprehensive perimeter treatment creates a barrier of protection against outside pest
activity. The barrier is applied each month for year-round pest prevention.
Nest and Web Removal
We thoroughly sweep the eaves of your house to ensure they are nest and web-free.
Interior Treatment
Our pest control technicians utilize a targeted approach to focus on specific moisture-prone
areas, such as the kitchen, bathrooms, laundry room, garage, and basement.
Crack and Crevice Treatment
A waterproof dust is applied with a bellows duster in the cracks and crevices where pest
activity is common.

Regular pest control service is most effective for maintaining a pest-free home throughout
the year. We offer prescheduled bi-monthly treatments to provide effective protection from
the most common household pests. If you notice any sign of pest activity between your
regularly scheduled visits, we will come back and take care of it.

Pest Library: Ants,Cockroaches,Rodents,Spiders,Stinging Insects,Bed Bugs,Silverfish,Fleas

Current discounts
$100 off first service for any recurring service

What To Expect From Our Commercial Pest Control:
In order to deliver the products or services your business offers in a way that keeps 
customers coming back, your commercial facility must be clean, welcoming, safe, and 
healthy. Discovering pests on your property creates problems in providing the exceptional 
services you want people to associate your company with. Pests contaminate their 
surroundings, create a space that people want to avoid, damage your building and the 
things inside, and spread harmful pathogens. Protecting your property from pests protects 
your business and helps you remain successful in your ventures. Banner Pest Services 
provides San Francisco Bay and East Bay Area and the surrounding areas with commercial pest 
control services customized to each business’s unique pest control needs.
With a background in commercial pest control and a commitment to delivering exceptional 
customer service, you can be certain that Banner Pest Services will provide you with the 
pest control you need to ensure your business stays pest-free. We offer customized treatment 
plans to each business we service so that you receive the personalized care necessary for 
the protection of your facility. To do this, we’ll thoroughly inspect your facility and 
property, then customize a treatment plan that targets the specific pests that are causing 
you problems.

Our Integrated Pest Management system will keep your business pest-free and running the way 
you need it to run. This program includes:
Regular inspections (monthly) of the interior and exterior of your property.
Identification of pests and a complete analysis of how they are acting in your area.
Comprehensive treatment of all affected areas and the implementation of protection measures 
to control the future emergence of pests on your property.
Continued visits to evaluate the efficiency of our treatment methods and adjustments to current 
methods if needed.

Facilities We Service:
Apartment Complexes
Office Buildings
Hotels
Restaurants
Healthcare Facilities
Dealerships
Storage Facilities
And More!

When you call the book_appointment function, please format the paramaters like this:
{
    "date": "2021-09-29",
    "time": "12:00"
}
The "date" parameter has to be in that format.
"""

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

start_chat_log = [
    {"role": "system", "content": context},
]


def askgpt(question: str, chat_log: list = None) -> tuple[str, list]:
    # If there is no chat log, start with the context
    if chat_log is None:
        chat_log = start_chat_log

    chat_log = chat_log + [{"role": "user", "content": question}]

    response = openAI_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=chat_log,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Check if the model wanted to call a function
    if tool_calls:
        available_functions = {
            "book_appointment": {
                "function": book_appointment,
                "parameters": ["date", "time"],
            },
            "end_conversation": {
                "function": end_conversation,
                "parameters": [],
            },
            "get_current_date_and_time": {
                "function": get_current_date_and_time,
                "parameters": [],
            },
        }

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

                function_response = function_to_call(**function_args)
                chat_log.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        # get a new response from the model where it can see the function response
        second_response = openAI_client.chat.completions.create(
            model="gpt-3.5-turbo-1106", messages=chat_log
        )

        answer = second_response.choices[0].message.content
    else:
        answer = response.choices[0].message.content

    chat_log = chat_log + [{"role": "assistant", "content": answer}]
    pretty_print_conversation(chat_log)
    return answer, chat_log


async def send_message(content: str, sender_number: str, twilio_number: str) -> None:
    message = twilio_client.messages.create(
        body=content,
        from_=twilio_number,
        to=sender_number,
    )
    return


def book_appointment(date: str, time: str) -> str:
    print("Booking Appointment...")
    return json.dumps({"date booked": date, "time booked": time})


def end_conversation():
    session.clear()
    print("Conversation Ended")
    return json.dumps({"end conversation": True})


def get_current_date_and_time() -> str:
    current_date_time = datetime.now()
    return current_date_time.isoformat()


def pretty_print_conversation(messages):
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

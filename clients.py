import os
from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client
from supabase import create_client

load_dotenv()

openAI_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# rcsdk = SDK(
#     os.getenv("RC_PROD_CLIENT_ID"),
#     os.getenv("RC_PROD_CLIENT_SECRET"),
#     os.getenv("RC_TEST_SERVER_URL"),
# )

# server_url = os.getenv("BASE_SERVER_URL")

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

# For production
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# For local testing
# supabase = create_client(os.getenv("SUPABASE_URL_TEST"), os.getenv("SUPABASE_KEY_TEST"))

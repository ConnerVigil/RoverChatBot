import os
from dotenv import load_dotenv
import sys
from ringcentral import SDK
import json

load_dotenv()

# https://developers.ringcentral.com/my-account.html#/applications

TEST_ACCOUNT_ID = 409190004
TEST_EXTENSION_ID = 101

rcsdk = SDK(
    os.getenv("RING_CENTRAL_CLIENT_ID"),
    os.getenv("RING_CENTRAL_CLIENT_SECRET"),
    os.getenv("RING_CENTRAL_SERVER_URL"),
)

platform = rcsdk.platform()
try:
    platform.login(jwt=os.getenv("RING_CENTRAL_JWT"))
except Exception as e:
    sys.exit("Unable to authenticate to platform: " + str(e))


def print_pretty(res: str):
    json_data = json.loads(res)
    json_string = json.dumps(json_data, indent=2, sort_keys=True)
    print(json_string)


# Get the account information
# r = platform.get(f'/restapi/v1.0/account/{TEST_ACCOUNT_ID}')
# print_pretty(r.text())


# create a subscription
# body = {
#     "eventFilters": [
#         f"/restapi/v1.0/account/{409190004}/telephony/sessions?missedCall=true",
#     ],
#     "deliveryMode": {
#         "transportType": "WebHook",
#         "address": "https://doe-up-muskox.ngrok-free.app/test",
#     },
#     "expiresIn": 60,
# }
# r = platform.post("/restapi/v1.0/subscription", body)
# print_pretty(r.text())

# get a list of subscriptions
# resp = platform.get("/restapi/v1.0/subscription")
# print_pretty(resp.text())


# List Company Phone Numbers
# r = platform.get(
#     f"/restapi/v1.0/account/{TEST_ACCOUNT_ID}/phone-number"
# )
# print_pretty(r.text())

import os
from dotenv import load_dotenv
import sys
from ringcentral import SDK

load_dotenv()

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

resp = platform.get("/restapi/v1.0/subscription")
jsonObj = resp.json()

for record in jsonObj.records:
    print(f"| Extension: {record.id}", end="")
    print(f"| Name: {record.uri}", end="")
    print(f"| Type: {record.type}")


# How to create a subscription
# POST BODY
body = {"eventFilters": ["<ENTER VALUE>"], "expiresIn": 000}

platform.login(os.environ["username"], os.environ["extension"], os.environ["password"])
r = platform.post("/restapi/v1.0/subscription", body)
# PROCESS RESPONSE

# JSON
# POST /restapi/v1.0/subscription
{
    "eventFilters": [
        "/restapi/v1.0/account/~/extension/~/presence",
        "/restapi/v1.0/account/~/extension/~/message-store",
        "/restapi/v1.0/account/~/telephony/sessions",
        "/restapi/v1.0/account/~/extension/~/presence?detailedTelephonyState=true&sipData=true",
    ],
    "deliveryMode": {
        "transportType": "WebHook",
        "address": "https://consumer-host.example.com/consumer/path",
    },
}

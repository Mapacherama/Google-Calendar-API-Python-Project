import vonage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

VONAGE_API_KEY = os.getenv("VONAGE_API_KEY")
VONAGE_API_SECRET = os.getenv("VONAGE_API_SECRET")

# Initialize Vonage client
client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
sms = vonage.Sms(client)

responseData = sms.send_message(
    {
        "from": "Vonage APIs",
        "to": "31621822756",
        "text": "This is a test message sent using the Vonage SMS API",
    }
)

if responseData["messages"][0]["status"] == "0":
    print("Message sent successfully.")
else:
    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
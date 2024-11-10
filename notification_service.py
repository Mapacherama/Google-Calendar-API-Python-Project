import os
import time
from dotenv import load_dotenv
from fastapi import HTTPException
from win10toast_click import ToastNotifier
import vonage

load_dotenv()
toaster = ToastNotifier()

SENDER_NAME = "EventNotifier"
VONAGE_API_KEY = os.getenv("VONAGE_API_KEY")
VONAGE_API_SECRET = os.getenv("VONAGE_API_SECRET")
USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER")

client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
sms = vonage.Sms(client)

def send_sms_notification(sms_body):
    try:
        responseData = sms.send_message({
            "from": SENDER_NAME,
            "to": USER_PHONE_NUMBER,
            "text": sms_body,
        })
        if responseData["messages"][0]["status"] == "0":
            print("SMS sent successfully.")
        else:
            print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
            raise HTTPException(status_code=500, detail="Failed to send SMS")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SMS")

def snooze_notification(summary, delay=600):
    time.sleep(delay)
    toaster.show_toast("Snoozed Reminder", f"{summary} reminder again!", duration=5)
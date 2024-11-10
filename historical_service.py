from datetime import datetime
from random import randint

import requests

from calendar_service import create_event

def add_historical_event_to_calendar(start_time: str, end_time: str, reminder_minutes: int, random_fact: bool = False):
    if random_fact:
        month = randint(1, 12)
        day = randint(1, 28)
        url = f"http://history.muffinlabs.com/date/{month}/{day}"
        selected_date = f"{month}/{day}"
    else:
        today = datetime.now().strftime("%m/%d")
        url = f"http://history.muffinlabs.com/date/{today}"
        selected_date = today
    
    response = requests.get(url)
    if response.status_code != 200:
        return {"message": "Failed to fetch data from the historical API"}

    data = response.json()
    if not data or "data" not in data or "Events" not in data["data"]:
        return {"message": "No historical events found."}

    event_info = data["data"]["Events"][0]
    year = event_info["year"]
    event_text = event_info["text"]
    
    summary = f"Historical Event on {selected_date}: {event_text} ({year})"
    description = f"This event happened on {selected_date} in {year}: {event_text}"

    event = create_event(summary, description, start_time, end_time, reminder_minutes)
    return event
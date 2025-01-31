from datetime import datetime
from random import randint

import requests

from calendar_service import create_event
from gemini_service import chat_with_gemini

def add_historical_event_to_calendar(start_time: str, end_time: str, reminder_minutes: int, random_fact: bool = False, use_ai: bool = False):
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
    
    if use_ai:
        ai_prompt = f"""
        Provide a detailed and engaging summary of the historical event: "{event_text}" that occurred in {year}.
        Add interesting context, global impact, and why it still matters today. Make it compelling and insightful.
        """
        ai_description = chat_with_gemini(ai_prompt)
        description += f"\n\n💡 AI Insight: {ai_description}"

    event = create_event(summary, description, start_time, end_time, reminder_minutes)
    return event
import time
from googleapiclient.discovery import build
from auth import authenticate_google_calendar
from win10toast_click import ToastNotifier
from typing import Optional
import requests
from datetime import datetime

toaster = ToastNotifier()

def snooze_notification(summary, delay=600):
    time.sleep(delay)
    toaster.show_toast("Snoozed Reminder", f"{summary} reminder again!", duration=5)

def get_calendar_service():
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)
    return service

def list_upcoming_events():
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId='primary',
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return events

def create_event(summary: str, description: str, start_time: str, end_time: str, is_all_day: bool = False):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'location': 'Online',
        'description': description,
    }

    if is_all_day:
        event['start'] = {'date': start_time}
        event['end'] = {'date': end_time}
    else:
        event['start'] = {
            'dateTime': start_time,
            'timeZone': 'Europe/Amsterdam',
        }
        event['end'] = {
            'dateTime': end_time,
            'timeZone': 'Europe/Amsterdam',
        }

    event = service.events().insert(calendarId='primary', body=event).execute()

    toaster.show_toast(
        "Event Created", 
        f"{summary} on {start_time}", 
        duration=5, 
        callback_on_click=lambda: snooze_notification(summary)
    )

    return event

def update_event(event_id: str, summary: Optional[str] = None, description: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None):
    service = get_calendar_service()
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    if summary:
        event['summary'] = summary
    if description:
        event['description'] = description
    if start_time:
        event['start'] = {'dateTime': start_time, 'timeZone': 'Europe/Amsterdam'}
    if end_time:
        event['end'] = {'dateTime': end_time, 'timeZone': 'Europe/Amsterdam'}

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

    toaster.show_toast(
        "Event Updated", 
        f"{event['summary']} on {event['start']['dateTime']}", 
        duration=5, 
        callback_on_click=lambda: snooze_notification(event['summary'])
    )

    return {"message": "Event updated", "updated_event": updated_event}

def delete_event(event_id: str):
    service = get_calendar_service()
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()

        toaster.show_toast(
            "Event Deleted", 
            f"Event ID {event_id} deleted", 
            duration=5, 
            callback_on_click=lambda: snooze_notification("Deleted Event")
        )

        return {"message": f"Event with ID {event_id} deleted successfully"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def add_historical_event_to_calendar():
    today = datetime.now().strftime("%m/%d")
    url = f"http://history.muffinlabs.com/date/{today}"
    response = requests.get(url)
    data = response.json()

    if not data or "data" not in data or "Events" not in data["data"]:
        return {"message": "No historical events found for today."}

    event_info = data["data"]["Events"][0]
    year = event_info["year"]
    event_text = event_info["text"]

    summary = f"Historical Event: {event_text} ({year})"
    description = f"This event happened on this day in {year}: {event_text}"
    start_time = datetime.now().strftime("%Y-%m-%d")
    end_time = start_time

    event = create_event(summary, description, start_time, end_time, is_all_day=True)
    return event

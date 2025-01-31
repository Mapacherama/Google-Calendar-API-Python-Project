import time
from fastapi import HTTPException
from googleapiclient.discovery import build
from auth import authenticate_google_calendar
from win10toast_click import ToastNotifier
from typing import Optional
from dotenv import load_dotenv

from notification_service import snooze_notification
from gemini_service import chat_with_gemini  # Import AI helper

load_dotenv()
toaster = ToastNotifier()

def get_calendar_service():
    creds = authenticate_google_calendar()
    return build('calendar', 'v3', credentials=creds)


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

def create_event(
    summary: str, 
    description: str, 
    start_time: str, 
    end_time: str, 
    reminder_minutes: int, 
    weather_info=None
):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Amsterdam',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Amsterdam',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': reminder_minutes},
            ],
        },
    }

    if weather_info:
        weather_description = (
            f"\n\nWeather Forecast:\n"
            f"Temperature: {weather_info['temperature']}°C\n"
            f"Weather: {weather_info['weather']}\n"
            f"Wind Speed: {weather_info['wind_speed']} m/s\n"
            f"Humidity: {weather_info['humidity']}%"
        )
        event['description'] += weather_description

    try:
        service = authenticate_google_calendar()
        print("Google Calendar Service:", service)  # Debugging line
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

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
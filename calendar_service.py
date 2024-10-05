from googleapiclient.discovery import build
from auth import authenticate_google_calendar

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

def create_event(summary: str, description: str, start_time: str, end_time: str):
    service = get_calendar_service()

    event = {
        'summary': summary,
        'location': 'Online',
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

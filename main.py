from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from typing import Optional
from calendar_service import (
    add_historical_event_to_calendar, 
    add_manga_chapter_to_calendar,
    get_mindfulness_quote,
    get_motivational_quote,
    get_next_airing_episode, 
    list_upcoming_events, 
    create_event,
    send_sms_notification, 
    update_event, 
    delete_event
)
from auth import authenticate_google_calendar
from pytz import timezone

from utils import convert_timestamp_to_iso

app = FastAPI()

@app.get("/events", summary="List Upcoming Events", tags=["Calendar"])
def get_upcoming_events():
    events = list_upcoming_events()
    if not events:
        return {"message": "No upcoming events found"}
    return events

@app.post("/create-event", summary="Create Event", tags=["Calendar"])
def schedule_event(
    summary: str, 
    description: Optional[str] = None, 
    start_time: str = "2024-10-10T10:00:00-07:00", 
    end_time: str = "2024-10-10T11:00:00-07:00"
):
    event = create_event(summary, description, start_time, end_time)
    return {"message": "Event created", "event": event}

@app.put("/update-event/{event_id}", summary="Update Event", tags=["Calendar"])
def modify_event(
    event_id: str, 
    summary: str, 
    description: Optional[str] = None, 
    start_time: str = "2024-10-10T10:00:00-07:00", 
    end_time: str = "2024-10-10T11:00:00-07:00"
):
    updated_event = update_event(event_id, summary, description, start_time, end_time)
    return {"message": "Event updated", "updated_event": updated_event}

@app.delete("/delete-event/{event_id}", summary="Delete Event", tags=["Calendar"])
def remove_event(event_id: str):
    result = delete_event(event_id)
    return result

from pytz import timezone

@app.post("/add-historical-event", summary="Add Historical Event", tags=["Calendar"])
def add_historical_event(
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    random_fact: bool = False
):
    event = add_historical_event_to_calendar(start_time, end_time, random_fact)
    if "message" in event:
        return {"message": event["message"]}
    return {"message": "Historical event added", "event": event}

@app.post("/add-mangadex-chapter", summary="Add MangaDex Chapter Event", tags=["Manga"])
def add_mangadex_chapter(
    manga_title: str, 
    start_time: str = "2024-10-10T18:00:00-07:00", 
    end_time: str = "2024-10-10T19:00:00-07:00",
    reminder_minutes: Optional[int] = 10
):
    result = add_manga_chapter_to_calendar(manga_title, start_time, end_time, reminder_minutes)
    if "message" in result:
        return {"message": result["message"]}
    return {"message": "Manga chapter event added", "event": result}

# New authentication endpoint for Google Calendar
@app.get("/authenticate", summary="Authenticate Google Calendar", tags=["Auth"])
def google_calendar_authenticate():
    creds = authenticate_google_calendar()
    if creds:
        return {"message": "Authentication successful, token.json created"}
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/schedule-mindfulness-event", summary="Schedule Mindfulness Event with SMS", tags=["Mindfulness", "Calendar"])
def schedule_mindfulness_event(
    summary: str = "Mindfulness Reminder", 
    description: Optional[str] = None, 
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'), 
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=90)).strftime('%Y-%m-%dT%H:%M:%S%z'), 
    reminder_minutes: int = 10
):
    try:
        quote = get_mindfulness_quote()
        
        if not description:
            description = f"Mindfulness Quote of the Day: {quote}"
        
        event = create_event(summary, description, start_time, end_time, reminder_minutes)
        
        sms_body = f"Reminder: {summary}. Quote: {quote}"
        send_sms_notification(sms_body)

        return {
            "message": "Mindfulness event created and SMS sent",
            "event": event,
            "quote": quote
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule-motivational-event", summary="Schedule Motivational Event with SMS", tags=["Motivation", "Calendar"])
def schedule_motivational_event(
    summary: str = "Motivational Reminder", 
    description: Optional[str] = None, 
    start_time: str = "2024-10-10T10:00:00-07:00", 
    end_time: str = "2024-10-10T11:00:00-07:00"
):
    try:
        quote = get_motivational_quote()
        
        if not description:
            description = f"Motivational Quote of the Day: {quote}"
        
        event = create_event(summary, description, start_time, end_time)
        
        sms_body = f"Reminder: {summary}. Quote: {quote}"
        send_sms_notification(sms_body)

        return {
            "message": "Motivational event created and SMS sent",
            "event": event,
            "quote": quote
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/add-anime-episode", summary="Add Anime Episode Event", tags=["Anime"])
def add_anime_episode(
    anime_title: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None
):
    try:
        anime_info = get_next_airing_episode(anime_title)
        if "message" in anime_info:
            return {"message": anime_info["message"]}
        
        airing_date = convert_timestamp_to_iso(anime_info["airing_at"])
        start_time = start_time or airing_date
        end_time = end_time or (datetime.fromisoformat(start_time) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")

        summary = f"New Episode of {anime_info['title']} (Episode {anime_info['episode']})"
        description = f"The next episode of {anime_info['title']} airs at {airing_date}."
        
        event = create_event(summary, description, start_time, end_time)
        
        sms_body = f"New Episode Alert: {summary} on {start_time}. Check your calendar for details."
        send_sms_notification(sms_body)

        return {
            "message": "Anime episode event added and SMS notification sent.",
            "event": event,
            "episode_info": {
                "title": anime_info['title'],
                "episode": anime_info['episode'],
                "airing_at": airing_date
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True)

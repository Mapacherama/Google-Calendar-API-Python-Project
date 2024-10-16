from fastapi import FastAPI, Request, HTTPException
from typing import Optional
from calendar_service import (
    add_historical_event_to_calendar, 
    add_manga_chapter_to_calendar, 
    list_upcoming_events, 
    create_event, 
    update_event, 
    delete_event
)
from auth import authenticate_google_calendar

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

@app.post("/add-historical-event", summary="Add Historical Event", tags=["Calendar"])
def add_historical_event():
    event = add_historical_event_to_calendar()
    if "message" in event:
        return {"message": event["message"]}
    return {"message": "Historical event added", "event": event}

@app.post("/add-mangadex-chapter", summary="Add MangaDex Chapter Event", tags=["Manga"])
def add_mangadex_chapter(manga_title: str):
    result = add_manga_chapter_to_calendar(manga_title)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True)

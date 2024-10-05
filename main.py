from fastapi import FastAPI
from typing import List, Optional
from calendar_service import list_upcoming_events, create_event

app = FastAPI()

@app.get("/events", summary="List Upcoming Events", tags=["Calendar"])
def get_upcoming_events():
    events = list_upcoming_events()
    if not events:
        return {"message": "No upcoming events found"}
    return events

@app.post("/create-event", summary="Create Event", tags=["Calendar"])
def schedule_event(summary: str, description: Optional[str] = None, start_time: str = "2024-10-10T10:00:00-07:00", end_time: str = "2024-10-10T11:00:00-07:00"):
    event = create_event(summary, description, start_time, end_time)
    return {"message": "Event created", "event": event}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True)

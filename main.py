from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from typing import Optional
from anime_service import get_next_airing_episode
from calendar_service import (
    list_upcoming_events, 
    create_event,
    update_event, 
    delete_event
)
from auth import authenticate_google_calendar
from pytz import timezone
from helpers import Utils
from historical_service import add_historical_event_to_calendar
from manga_service import add_manga_chapter_to_calendar, get_latest_manga_chapter, open_chapter, search_manga, wait_until
from mindfulness_service import get_mindfulness_quote
from motivational_service import get_motivational_quote
from movie_service import fetch_movie_recommendation
from notification_service import send_sms_notification
from spotify_service import notify_spotify_playback
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
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=90)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    reminder_minutes: int = 10
):
    event = create_event(summary, description, start_time, end_time, reminder_minutes)
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
def add_historical_event(
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=90)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    reminder_minutes: Optional[int] = 10,
    random_fact: bool = False,
    reminder_track_uri: Optional[str] = None
):
    try:
        event = add_historical_event_to_calendar(start_time, end_time, reminder_minutes, random_fact)
        
        if reminder_track_uri:
            print("Calling notify_spotify_playback for reminder with track_uri:", reminder_track_uri)
            notify_spotify_playback(track_uri=reminder_track_uri, play_before=reminder_minutes)

        if "message" in event:
            return {"message": event["message"]}

        return {
            "message": "Historical event added, with Spotify playback scheduled if URIs were provided.",
            "event": event
        }
    except Exception as e:
        print("Error adding historical event:", str(e))  # Log the error
        raise HTTPException(status_code=500, detail="Failed to add historical event.")

@app.post("/add-mangadex-chapter", summary="Add MangaDex Chapter Event", tags=["Manga"])
def add_mangadex_chapter(
    manga_title: str,
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    reminder_minutes: Optional[int] = 10,
    chapter_url: Optional[str] = None
):
    start_time = start_time[:-2] + ':' + start_time[-2:]
    end_time = end_time[:-2] + ':' + end_time[-2:]

    if chapter_url:
        summary = f"Reading Chapter of {manga_title}"
        description = f"Read the chapter here: {chapter_url}"
        target_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
        print(f"Scheduling to open chapter URL at {target_time}")
        wait_until(target_time)
        open_chapter(chapter_url)
    else:
        manga_info = search_manga(manga_title)
        if "message" in manga_info:
            return {"message": manga_info["message"]}

        chapter_info = get_latest_manga_chapter(manga_info["id"])
        if "message" in chapter_info:
            return {"message": chapter_info["message"]}

        summary = f"New Chapter of {manga_info['title']} Available!"
        chapter_url = chapter_info['chapter_url']
        description = f"Read the latest chapter here: {chapter_url}"
        target_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
        print(f"Scheduling to open latest chapter URL at {target_time}")
        wait_until(target_time)
        open_chapter(chapter_url)

    event = create_event(summary, description, start_time, end_time, reminder_minutes)
    return {
        "message": "Manga chapter event handled successfully.",
        "event": event,
        "chapter_url": chapter_url
    }

@app.get("/authenticate", summary="Authenticate Google Calendar", tags=["Auth"])
def google_calendar_authenticate():
    creds = authenticate_google_calendar()
    if creds:
        return {"message": "Authentication successful, token.json created"}
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/schedule-mindfulness-event", summary="Schedule Mindfulness Event", tags=["Mindfulness", "Calendar"])
def schedule_mindfulness_event(
    summary: str = "Mindfulness Reminder", 
    description: Optional[str] = None, 
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'), 
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=90)).strftime('%Y-%m-%dT%H:%M:%S%z'), 
    pre_event_offset: int = 10,
    pre_event_track_uri: Optional[str] = None,
    during_event_track_uri: Optional[str] = None,
    post_event_offset: int = 10,
    post_event_track_uri: Optional[str] = None
):
    try:
        quote = get_mindfulness_quote()
        
        if not description:
            description = f"Mindfulness Quote of the Day: {quote}"
        
        event = create_event(summary, description, start_time, end_time, pre_event_offset)
        
        start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
        
        if pre_event_track_uri:
            pre_event_time = (start_dt - timedelta(minutes=pre_event_offset)).strftime('%Y-%m-%dT%H:%M:%S%z')
            notify_spotify_playback(track_uri=pre_event_track_uri, play_time=pre_event_time)

        if during_event_track_uri:
            during_event_time = start_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
            notify_spotify_playback(track_uri=during_event_track_uri, play_time=during_event_time)

        if post_event_track_uri:
            post_event_time = (start_dt + timedelta(minutes=post_event_offset)).strftime('%Y-%m-%dT%H:%M:%S%z')
            notify_spotify_playback(track_uri=post_event_track_uri, play_time=post_event_time)

        return {
            "message": "Mindfulness event created, and individual Spotify playlists scheduled based on specified times.",
            "event": event,
            "quote": quote
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule-motivational-event", summary="Schedule Motivational Event", tags=["Motivation", "Calendar"])
def schedule_motivational_event(
    summary: str = "Motivational Reminder", 
    description: Optional[str] = None, 
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'), 
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=90)).strftime('%Y-%m-%dT%H:%M:%S%z'), 
    reminder_minutes: int = 10,
    track_uri: Optional[str] = None
):
    print("Inside schedule_motivational_event")
    print("track_uri:", track_uri)  
    try:
        quote = get_motivational_quote()
        
        if not description:
            description = f"Motivational Quote of the Day: {quote}"
        
        event = create_event(summary, description, start_time, end_time, reminder_minutes)
        
        if track_uri:
            start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
            reminder_time = (start_dt - timedelta(minutes=reminder_minutes)).strftime('%Y-%m-%dT%H:%M:%S%z')
            print("Calling notify_spotify_playback with track_uri:", track_uri)
            notify_spotify_playback(track_uri=track_uri, play_time=reminder_time)
        
        return {
            "message": "Motivational event created, and Spotify playback scheduled (if track URI provided).",
            "event": event,
            "quote": quote
        }
    except Exception as e:
        print("Exception in schedule_motivational_event:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-anime-episode", summary="Add Anime Episode Event", tags=["Anime"])
def add_anime_episode(
    anime_title: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None,
    reminder_minutes: int = 10,
    track_uri: Optional[str] = None
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
        
        event = create_event(summary, description, start_time, end_time, reminder_minutes)
        
        if track_uri:
            print("Calling notify_spotify_playback for Anime Episode Event with track_uri:", track_uri)
            notify_spotify_playback(track_uri=track_uri, play_before=reminder_minutes)
        
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
        
@app.post("/schedule-movie-session", summary="Schedule Daytime Movie Session", tags=["Entertainment", "Calendar"])
def schedule_movie_session(
    genre: str = "Action", 
    rating: float = 7.0, 
    period: str = "1990s", 
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(hours=10)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    reminder_minutes: int = 10,
    track_uri: Optional[str] = None
):
    try:
        start_date, end_date = Utils.parse_period(period)
        movie = fetch_movie_recommendation(genre=genre, rating=rating, period=(start_date, end_date))
        
        print("Response from function:", movie)
        
        if not movie:
            return {"message": "No movie recommendation found. Try adjusting your filters!"}
        
        summary = f"{movie['title']} ({movie['release_date'][:4]}) - {genre}"
        description = f"Today's movie: {movie['title']} - Rating: {movie['vote_average']} | Enjoy some 'Brain' time!"
        
        event = create_event(summary, description, start_time, end_time, reminder_minutes)
        
        if track_uri:
            print("Calling notify_spotify_playback for Movie Session with track_uri:", track_uri)
            notify_spotify_playback(track_uri=track_uri, play_before=reminder_minutes)
        
        sms_body = f"Movie Recommendation: {movie['title']} - Check your calendar for details!"
        send_sms_notification(sms_body)

        return {
            "message": "Movie session scheduled successfully!",
            "event": event,
            "movie": {
                "title": movie["title"],
                "year": movie["release_date"][:4],
                "rating": movie["vote_average"],
                "genre": genre
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True)

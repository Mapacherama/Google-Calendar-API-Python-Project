from datetime import datetime, timedelta
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
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
from manga_service import get_latest_manga_chapter, open_chapter, search_manga
from mindfulness_service import get_mindfulness_quote
from motivational_service import get_motivational_quote
from movie_service import fetch_movie_recommendation, recommend_movie_with_ai
# from notification_service import send_sms_notification
from spotify_service import notify_spotify_playback
from weather_service import fetch_weather
from gemini_service import chat_with_gemini

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

@app.get("/recommendations", summary="AI-Driven Personalized Recommendations", tags=["Recommendations"])
def get_recommendations(
    user_id: Optional[str] = None, 
    num_suggestions: int = 3
):
    """
    Generate personalized event, playlist, and video recommendations.
    """
    try:
        # Fetch historical events from the calendar
        historical_events = list_upcoming_events()

        # Generate Event Suggestions
        suggested_events = Utils.generate_event_suggestions(historical_events, num_suggestions)

        # Recommend Spotify Playlists
        spotify_playlists = Utils.recommend_spotify_playlists(historical_events, num_suggestions)

        # Recommend YouTube Videos
        youtube_videos = Utils.recommend_youtube_videos(historical_events, num_suggestions)

        return {
            "message": "Personalized recommendations generated successfully.",
            "suggested_events": suggested_events,
            "spotify_playlists": spotify_playlists,
            "youtube_videos": youtube_videos
        }
    except Exception as e:
        logging.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations.")
    
@app.post("/schedule-focus-blocks", summary="Schedule Focus Blocks with AI Coaching", tags=["Productivity", "Calendar"])
def schedule_focus_blocks(
    num_blocks: int = 3, 
    focus_duration: int = 90, 
    break_duration: int = 10,
    start_time: Optional[str] = None,
    summary_prefix: str = "Focus Block"
):
    """
    Schedule 90-minute focus blocks followed by 10-minute breaks.
    
    Now enhanced with AI-generated productivity coaching.
    
    Args:
        - num_blocks: Number of focus blocks to create.
        - focus_duration: Duration of each focus block (in minutes).
        - break_duration: Duration of each break (in minutes).
        - start_time: Optional start time (default is now).
        - summary_prefix: Title prefix for focus events.
    """
    try:
        # Default start time to now if not provided
        current_time = datetime.now(timezone('Europe/Amsterdam')) if not start_time else datetime.strptime(
            start_time, "%Y-%m-%dT%H:%M:%S%z"
        )

        events = []
        ai_coaching_tips = []

        for i in range(num_blocks):
            # Generate AI productivity advice for this focus session
            ai_tip = chat_with_gemini(
                f"I'm about to start a {focus_duration}-minute deep work session. "
                "Give me a quick productivity tip to maximize focus."
            )
            ai_coaching_tips.append(ai_tip)

            # Schedule Focus Block
            focus_start = current_time
            focus_end = focus_start + timedelta(minutes=focus_duration)
            focus_summary = f"{summary_prefix} {i+1}"
            focus_event = create_event(focus_summary, ai_tip, focus_start.isoformat(), focus_end.isoformat(), 10)
            events.append(focus_event)

            # Schedule Break
            break_start = focus_end
            break_end = break_start + timedelta(minutes=break_duration)
            break_summary = f"Break {i+1}"
            break_event = create_event(break_summary, "Take a short break", break_start.isoformat(), break_end.isoformat(), 5)
            events.append(break_event)

            # Update current time to after the break
            current_time = break_end

        return {
            "message": f"{num_blocks} focus blocks scheduled successfully with AI coaching.",
            "events": events,
            "ai_coaching_tips": ai_coaching_tips  # Include AI-generated deep work tips
        }
    except Exception as e:
        logging.error(f"Error scheduling focus blocks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule focus blocks.")


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
    background_tasks: BackgroundTasks,
    manga_title: str,
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    reminder_minutes: Optional[int] = 10,
    chapter_url: Optional[str] = None
):
    try:
        start_time_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError as e:
        return {"error": f"Invalid time format: {str(e)}"}

    delay_seconds = (start_time_dt - datetime.now(timezone('Europe/Amsterdam'))).total_seconds()
    if delay_seconds < 0:
        return {"error": "The start time is in the past. Please provide a future time."}

    if chapter_url:
        summary = f"Reading Chapter of {manga_title}"
        description = f"Read the chapter here: {chapter_url}"
        print(f"Scheduling to open chapter URL at {start_time_dt}")
        background_tasks.add_task(open_chapter, chapter_url, start_time_dt)
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
        print(f"Scheduling to open latest chapter URL at {start_time_dt}")
        background_tasks.add_task(open_chapter, chapter_url, start_time_dt)

    # Create Google Calendar Event
    event = create_event(summary, description, start_time, end_time, reminder_minutes)
    print(f"Google Calendar Event Created: {event}")

    return {
        "message": "Manga chapter event scheduled successfully.",
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
    track_uri: Optional[str] = None,
    use_ai: bool = False
):
    print("Inside schedule_motivational_event")
    print("track_uri:", track_uri)  
    try:
        if use_ai:
            quote = chat_with_gemini(
                f"I'm about to start a high-energy motivational session and need a truly powerful quote from a legendary athlete. "
                "The quote should ignite passion, resilience, and relentless pursuit of greatness—something that pushes me beyond limits" 
                "and fuels my determination. Share a quote from a world-class athlete known for their mental toughness, "
                "discipline, and drive to win, along with their name and a brief context about why it's impactful."
            )
            print("Gemini AI quote:", quote)
        else:
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
        
        airing_date = Utils.convert_timestamp_to_iso(anime_info["airing_at"])
        start_time = start_time or airing_date
        end_time = end_time or (datetime.fromisoformat(start_time) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")

        summary = f"New Episode of {anime_info['title']} (Episode {anime_info['episode']})"
        description = f"The next episode of {anime_info['title']} airs at {airing_date}."
        
        event = create_event(summary, description, start_time, end_time, reminder_minutes)
        
        if track_uri:
            print("Calling notify_spotify_playback for Anime Episode Event with track_uri:", track_uri)
            notify_spotify_playback(track_uri=track_uri, play_before=reminder_minutes)
        
        # sms_body = f"New Episode Alert: {summary} on {start_time}. Check your calendar for details."
        # send_sms_notification(sms_body)

        return {
            "message": "Anime episode event added",
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
    track_uri: Optional[str] = None,
    use_ai: bool = False
):
    try:
            
        start_date, end_date = Utils.parse_period(period)
        if use_ai:
            movie = recommend_movie_with_ai(genre=genre, rating=rating, period=(start_date, end_date))
        else:
            movie = fetch_movie_recommendation(genre=genre, rating=rating, period=(start_date, end_date))
        
        print("Response from function:", movie)
        print("title of the movie:", movie["title"])
        
        if not movie:
            return {"message": "No movie recommendation found. Try adjusting your filters!"}
        
        if use_ai:
            # AI-generated movie format
            title_part = movie["title"].split("\n")[0]
            print("title_part:", title_part)
            summary = f"{title_part} - {genre}"
            description = f"Today's movie: {title_part} | {movie['title'].split('* Description: ')[-1]}"
            print("Summary:", summary)
            print("Description:", description)
        else:
            summary = f"{movie['title']} ({movie['release_date'][:4]}) - {genre}"
            description = f"Today's movie: {movie['title']} - Rating: {movie['vote_average']} | Enjoy some 'Brain' time!"
        
        event = create_event(summary, description, start_time, end_time, reminder_minutes)
        
        if track_uri:
            print("Calling notify_spotify_playback for Movie Session with track_uri:", track_uri)
            notify_spotify_playback(track_uri=track_uri, play_before=reminder_minutes)
            
        if use_ai:
    # AI-generated movie handling
            movie_title = movie["title"].split("\n")[0]  # Extract only the title
            movie_year = movie.get("year", "Unknown Year")  # AI might not return a proper year

            return {
            "message": "Movie session scheduled successfully!",
            "event": event,
            "movie": {
                "title": movie_title,
                "year": movie_year,
                "rating": movie.get("rating", "N/A"),
                "genre": genre
            }
        }    
        else:    
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
    
@app.post("/schedule-running-event", summary="Schedule Running Event", tags=["Fitness", "Calendar"])
def schedule_running_event(
    city: str,
    start_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    end_time: str = (datetime.now(timezone('Europe/Amsterdam')) + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S%z'),
    reminder_minutes: int = 10,
):
    try:
        weather = fetch_weather(city)
        weather_details = (
            f"Weather during your run: {weather['temperature']}°C, {weather['weather']}. "
            f"Humidity: {weather['humidity']}%. Wind Speed: {weather['wind_speed']} m/s."
        )

        summary = "Running Session"
        description = f"Running in {city}. {weather_details}"

        event = create_event(summary, description, start_time, end_time, reminder_minutes)

        return {
            "message": "Running event scheduled successfully!",
            "event": event,
            "weather": weather
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule running event: {str(e)}")
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True)

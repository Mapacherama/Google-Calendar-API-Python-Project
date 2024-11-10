from datetime import datetime

from fastapi import HTTPException
import requests

def notify_spotify_playback(track_uri: str, play_time: str):
    spotify_url = "http://127.0.0.1:8000/schedule-playlist"
    
    params = {
        "playlist_uri": track_uri,
        "play_time": datetime.strptime(play_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M")
    }

    try:
        response = requests.get(spotify_url, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to schedule Spotify playback")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error scheduling Spotify playback")
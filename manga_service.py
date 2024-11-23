import requests
import webbrowser
import time
from datetime import datetime
from pytz import timezone

from calendar_service import create_event
from notification_service import send_sms_notification


def search_manga(title: str):
    url = f"https://api.mangadex.org/manga?title={title}"
    response = requests.get(url)
    data = response.json()

    if not data or "data" not in data:
        return {"message": "No manga found with that title."}

    manga = data["data"][0]
    manga_id = manga["id"]
    manga_title = manga["attributes"]["title"]["en"]

    return {"id": manga_id, "title": manga_title}


def get_latest_manga_chapter(manga_id: str):
    url = f"https://api.mangadex.org/chapter?manga={manga_id}&limit=1&translatedLanguage[]=en"
    response = requests.get(url)
    data = response.json()

    if not data or "data" not in data:
        return {"message": "No chapters found."}

    chapter = data["data"][0]
    chapter_title = chapter["attributes"]["title"]
    chapter_url = f"https://mangadex.org/chapter/{chapter['id']}"

    return {"chapter_title": chapter_title, "chapter_url": chapter_url}


def add_manga_chapter_to_calendar(manga_title: str, start_time: str, end_time: str, reminder_minutes: int, chapter_url: str = None):
    if chapter_url:
        summary = f"Reading Chapter of {manga_title}"
        description = f"Read the chapter here: {chapter_url}"
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

    start_time_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
    delay = (start_time_dt - datetime.now(timezone('Europe/Amsterdam'))).total_seconds()

    if delay > 0:
        time.sleep(delay)

    event = create_event(summary, description, start_time, end_time, reminder_minutes)
    webbrowser.open(chapter_url)

    return {
        "message": "Manga chapter event added.",
        "event": event,
        "chapter_url": chapter_url
    }
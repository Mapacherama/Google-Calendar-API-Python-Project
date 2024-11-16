import requests
import webbrowser  # {{ edit_1 }}

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


def add_manga_chapter_to_calendar(manga_title: str, start_time: str, end_time: str, reminder_minutes: int, manga_url: str = None):  # {{ edit_2 }}
    manga_info = search_manga(manga_title)
    if "message" in manga_info:
        return {"message": manga_info["message"]}

    chapter_info = get_latest_manga_chapter(manga_info["id"])
    if "message" in chapter_info:
        return {"message": chapter_info["message"]}

    summary = f"New Chapter of {manga_info['title']} Available!"
    description = f"Read the latest chapter here: {chapter_info['chapter_url']}"

    event = create_event(summary, description, start_time, end_time, reminder_minutes)

    sms_body = f"New Chapter of {manga_info['title']} available! Check your calendar for details."
    send_sms_notification(sms_body)

    if manga_url:  # {{ edit_3 }}
        webbrowser.open(manga_url)  # {{ edit_4 }}

    return {"message": "Manga chapter event added and SMS notification sent.", "event": event}
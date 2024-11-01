# todoist_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TODOIST_CLIENT_ID = os.getenv("TODOIST_CLIENT_ID")
TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET")
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

REDIRECT_URI = "http://localhost:7000/callback"

def get_auth_url():
    return (
        "https://todoist.com/oauth/authorize"
        f"?client_id={TODOIST_CLIENT_ID}"
        "&scope=data:read_write"
        f"&redirect_uri={REDIRECT_URI}"
    )

def exchange_code_for_token(code: str):
    token_url = "https://todoist.com/oauth/access_token"
    payload = {
        "client_id": TODOIST_CLIENT_ID,
        "client_secret": TODOIST_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        error_message = response.json().get("error", "Unknown error")
        raise Exception(f"Failed to retrieve access token: {error_message}")

def fetch_todoist_tasks():
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}"
    }
    response = requests.get("https://api.todoist.com/rest/v1/tasks", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch tasks from Todoist")
        return []
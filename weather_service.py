from fastapi import HTTPException
import requests
import os

def fetch_weather(city: str):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch weather data")
    
    data = response.json()
    weather_info = {
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "humidity": data["main"]["humidity"]
    }
    
    return weather_info
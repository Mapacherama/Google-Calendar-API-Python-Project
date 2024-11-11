import os
from random import choice
import requests

API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")

def get_mindfulness_quote():
    mindfulness_categories = [
        'calm',
        'courage',
        'fear',
        'happiness',
        'hope',
        'forgiveness',
        'freedom',
        'friendship',
        'inspirational',
        'love',
        'life',
        'health',
        'attitude',
        'beauty',
        'success'
    ]

    category = choice(mindfulness_categories)
    print(f"Selected Category: {category}")

    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
    
    response = requests.get(api_url, headers={'X-Api-Key': API_NINJAS_KEY})

    if response.status_code == 200:
        data = response.json()
        if data:
            quote = data[0].get("quote", "No quote available")
            author = data[0].get("author", "Unknown")
            return f"{quote} - {author}"
    else:
        print(f"Failed to retrieve quote. Status code: {response.status_code}, Response: {response.text}")
        return "Error retrieving mindfulness message, please try again later."
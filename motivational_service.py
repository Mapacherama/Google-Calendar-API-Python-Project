import requests


def get_motivational_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            quote = data[0]['q']
            author = data[0]['a']
            return f"{quote} - {author}"
        else:
            return "Unable to fetch a quote at the moment."
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return "Stay inspired and keep pushing!"
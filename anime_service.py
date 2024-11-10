import requests


def get_next_airing_episode(anime_title: str):
    url = "https://graphql.anilist.co"
    query = """
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            id
            title {
                romaji
                english
            }
            nextAiringEpisode {
                airingAt
                episode
            }
        }
    }
    """
    variables = {"search": anime_title}
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()
            media = data["data"]["Media"]
            if not media["nextAiringEpisode"]:
                return {"message": f"No upcoming episodes found for {anime_title}."}
            airing_at = media["nextAiringEpisode"]["airingAt"]
            episode = media["nextAiringEpisode"]["episode"]
            return {
                "title": media["title"]["romaji"] or media["title"]["english"],
                "airing_at": airing_at,
                "episode": episode
            }
        else:
            return {"message": "Failed to fetch anime details from AniList."}
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {"message": "An error occurred while fetching anime details."}
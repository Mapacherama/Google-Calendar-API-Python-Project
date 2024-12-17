from datetime import datetime

class Utils:
    @staticmethod
    def generate_event_suggestions(historical_events, num_suggestions):
        """
        Generate event suggestions based on historical events.
        """
        categories = ["fitness", "motivational talk", "social"]
        suggestions = [
            {"event": f"Join a {category} event", "time": datetime.now() + timedelta(days=i)}
            for i, category in enumerate(categories[:num_suggestions])
        ]
        return suggestions

    @staticmethod
    def recommend_spotify_playlists(historical_events, num_suggestions):
        """
        Recommend Spotify playlists based on historical event keywords.
        """
        keywords = [event.get("summary", "").split()[0] for event in historical_events if "summary" in event]
        playlists = [{"name": f"Top {kw} Playlist", "uri": f"spotify:playlist:{kw}123"} for kw in keywords[:num_suggestions]]
        return playlists

    @staticmethod
    def recommend_youtube_videos(historical_events, num_suggestions):
        """
        Recommend YouTube videos based on historical event categories.
        """
        videos = [
            {"title": "Best Motivational Talk", "url": "https://www.youtube.com/watch?v=example1"},
            {"title": "Top Fitness Routines", "url": "https://www.youtube.com/watch?v=example2"},
            {"title": "Relaxing Music for Focus", "url": "https://www.youtube.com/watch?v=example3"}
        ]
        return videos[:num_suggestions]


    def convert_timestamp_to_iso(airing_at: int):
        return datetime.fromtimestamp(airing_at).strftime("%Y-%m-%dT%H:%M:%S")

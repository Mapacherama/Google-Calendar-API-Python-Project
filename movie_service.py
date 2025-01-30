from random import choice
from typing import Optional
import requests
import os

BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_movies_with_high_ratings(
    min_rating: float = 7.0,
    vote_count: int = 50,
    release_start: str = '1990-01-01',
    release_end: str = '1999-12-31',
    genre_id: Optional[int] = None
):
    url = f"{BASE_URL}/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'sort_by': 'vote_average.desc',
        'vote_count.gte': vote_count,
        'vote_average.gte': min_rating,
        'primary_release_date.gte': release_start,
        'primary_release_date.lte': release_end,
        'page': 1
    }
    
    if genre_id:
        params['with_genres'] = genre_id

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Failed to fetch movie data: {response.status_code}")
        return []
    
import os
import google.generativeai as genai

# Load API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def recommend_movie_with_ai(genre: str, rating: float, period: str):
    """
    Uses Gemini AI to recommend a movie based on the given parameters.

    :param genre: Movie genre (e.g., "Action", "Comedy").
    :param rating: Minimum rating (e.g., 7.0).
    :param period: Time period for the movie (e.g., "1990s").
    :return: A dictionary with movie details or a fallback recommendation.
    """
    prompt = (
        f"Recommend a highly rated {genre} movie from the {period} with at least a {rating} IMDb rating. "
        "Include the title, release year, and a short description."
    )

    try:
        response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
        ai_text = response.text.strip()

        # Parse AI response (adjust based on actual AI response structure)
        movie = {"title": ai_text, "year": period, "rating": rating, "genre": genre}

        return movie

    except Exception as e:
        print(f"AI recommendation failed: {str(e)}")
        return {"title": "The Matrix", "year": 1999, "rating": 8.7, "genre": genre}  # Fallback movie    
    
def get_genre_id(genre_name):
    genre_map = {
        "Action": 28,
        "Adventure": 12,
        "Animation": 16,
        "Comedy": 35,
        "Crime": 80,
        "Documentary": 99,
        "Drama": 18,
        "Family": 10751,
        "Fantasy": 14,
        "Horror": 27,
        "Romance": 10749,
        "Science Fiction": 878,
        "Thriller": 53,
        "War": 10752,
        "Western": 37
    }
    genre_id = genre_map.get(genre_name)
    print("Genre ID for selected genre:", genre_id)  
    return genre_id    
    
def fetch_movie_recommendation(genre, rating, period):
    """
    Fetches a movie recommendation based on genre, rating, and period.

    Parameters:
        genre (str): The genre to filter movies.
        rating (float): Minimum rating for movies.
        period (tuple or str): A tuple with start and end dates (e.g., ("1990-01-01", "1999-12-31"))
                               or a single string if only one date range is intended.

    Returns:
        dict: Information about the recommended movie.
    """
    if isinstance(period, tuple) and len(period) == 2:
        start_date, end_date = period
    else:
        raise ValueError("Period should be a tuple with two date strings, e.g., ('1990-01-01', '1999-12-31')")

    genre_id = get_genre_id(genre)
    
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'sort_by': 'vote_average.desc',
        'vote_count.gte': 50,
        'vote_average.gte': rating,
        'primary_release_date.gte': start_date,
        'primary_release_date.lte': end_date,
        'with_genres': genre_id,
        'page': 1
    }
    
    response = requests.get(f"{BASE_URL}/discover/movie", params=params)

    if response.status_code == 200:
        movies = response.json().get('results', [])
        if movies:
            return choice(movies)
        else:
            return {"message": "No movies found with the specified criteria."}
    else:
        print(f"Failed to fetch movie data: {response.status_code}")
        return {"message": "Failed to retrieve movie recommendation."}
    
def get_genre_id(genre_name):
    """
    Returns the genre ID for a given genre name.
    """
    genre_map = {
        "Action": 28,
        "Adventure": 12,
        "Animation": 16,
        "Comedy": 35,
        "Crime": 80,
        "Documentary": 99,
        "Drama": 18,
        "Family": 10751,
        "Fantasy": 14,
        "Horror": 27,
        "Romance": 10749,
        "Science Fiction": 878,
        "Thriller": 53,
        "War": 10752,
        "Western": 37
    }
    return genre_map.get(genre_name, None)
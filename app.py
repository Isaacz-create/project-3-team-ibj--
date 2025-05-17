import os
import random
import requests
import gradio as gr
import ollama
from dotenv import load_dotenv

# Load API keys
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Predefined mood-to-movie IDs
MOOD_TO_MOVIE_IDS = {
    "happy": [13, 550, 278, 680, 105, 12, 293660],
    "sad": [424, 500, 578, 597, 807, 497, 266],
    "adventurous": [122, 98, 140607, 22, 120, 8587, 177572],
    "romantic": [194, 281, 348, 534, 12405, 12244, 227],
    "nostalgic": [11, 85, 9615, 11324, 100, 101, 581],
    "mystery": [274, 155, 807, 614, 345, 862, 915]
}

# Get movie info from TMDB
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data["title"],
            "overview": data["overview"],
            "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else ""
        }
    return None

# Generate text using Ollama
def generate_ai_description(mood, movies):
    movie_text = "\n".join(
        [f"Title: {movie['title']}\nOverview: {movie['overview']}" for movie in movies]
    )
    prompt = f"""
A user is feeling "{mood}". You've been given a list of movies. Explain in a fun and thoughtful way why these 3 movies are a great fit for that mood.

Movies:
{movie_text}
"""
    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

# Main function for Gradio
def recommend_movies(mood):
    mood = mood.lower().strip()
    if mood not in MOOD_TO_MOVIE_IDS:
        return f" Mood not found. Try one of: {', '.join(MOOD_TO_MOVIE_IDS.keys())}"

    movie_ids = random.sample(MOOD_TO_MOVIE_IDS[mood], 3)
    movies = [fetch_movie_details(mid) for mid in movie_ids if fetch_movie_details(mid)]

    if not movies:
        return " Couldn't fetch movie data."

    ai_summary = generate_ai_description(mood, movies)

    markdown = f"##  AI Insight for mood: '{mood.title()}'\n\n{ai_summary}\n\n---\n"
    for movie in movies:
        markdown += f"###  {movie['title']}\n{movie['overview']}\n"
        if movie['poster']:
            markdown += f"![Poster]({movie['poster']})\n"
        markdown += "---\n"

    return markdown

# Gradio UI
iface = gr.Interface(
    fn=recommend_movies,
    inputs=gr.Textbox(label="How are you feeling today? (e.g. happy, sad...)"),
    outputs=gr.Markdown(),
    title=" Mood-Based Movie Recommender",
    description="Enter a mood like Happy, Sad, Adventurous, Romantic, Nostalgic, or Mystery to get personalized movie recommendation."
)

iface.launch(share=True)

